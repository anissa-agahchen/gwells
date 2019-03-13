"""
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
import logging
import dateutil.parser

from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.db import transaction
from django.db.models import F

from gwells.models import ProvinceStateCode
from submissions.models import WellActivityCode
import submissions.serializers
from wells.models import Well, ActivitySubmission, WellStatusCode
from wells.serializers import WellStackerSerializer

import reversion

logger = logging.getLogger(__name__)


def overlap(a, b):
    """
    Checks to see if two casings intersect, or have identical start/end positions.
    """
    # If the casing start/end intersects
    intersect = (a[0] > b[0] and a[0] < b[1]) or (a[1] > b[0] and a[1] < b[1])
    # If the casings start or end in the same place
    overlap = (a[0] == b[0]) or (a[1] == b[1])
    return intersect or overlap


class StackWells():

    @transaction.atomic
    def process(self, filing_number) -> Well:
        """
        Take a submission, and use it to create/update a well entry.
        As a side effect of calling this method, a legacy well record may be created if required.
        """
        submission = ActivitySubmission.objects.get(
            filing_number=filing_number)
        if submission.well is not None:
            # If there's already a well, we update it
            return self._update_well_record(submission)
        # If there is as yet no well, we create one
        well = Well.objects.create()
        well = self._stack(ActivitySubmission.objects.filter(filing_number=filing_number), well)
        submission.well = well
        submission.save()
        return well

    @transaction.atomic
    def _create_legacy_submission(self, well: Well) -> None:
        """
        Using an existing well as a reference, create a legacy well record
        """
        # TODO: Deal with Lithology, LtsaOwner, AquiferWell etc. (This should
        # work magically if the serializers are implemented correctly)
        # Serialize the well.
        well_serializer = WellStackerSerializer(well)
        data = well_serializer.data
        # Retain the construction date.
        data['work_start_date'] = data.pop('construction_start_date', None)
        data['work_end_date'] = data.pop('construction_end_date', None)
        # Filter out None and '' values, they can interfere with validation.
        data = {k: v for (k, v) in data.items() if v is not None and v != ''}
        # Retain the well reference.
        data['well'] = well.well_tag_number
        # De-serialize the well into a submission.
        submission_serializer = submissions.serializers.WellSubmissionLegacySerializer(data=data)

        # Validate the data, throwing an exception on error.
        if submission_serializer.is_valid(raise_exception=True):
            # Save the submission.
            legacy = submission_serializer.save()
            return legacy
        return None

    def _series_overlaps(self, record, record_set):
        # Return True if a record overlaps with a list of records
        for other_record in record_set:
            if overlap((record.get('start'), record.get('end')),
                       (other_record.get('start'), other_record.get('end'))):
                return True
        return False

    def _merge_series(self, prev_series, next_series):
        # Remove old records that overlap with new records
        prev_series = [record for record in prev_series if not self._series_overlaps(record, next_series)]
        # Join the old with the new
        new = prev_series + next_series
        # Sort
        new.sort(key=lambda record: (record.get('start'), record.get('end')))
        return new

    @transaction.atomic
    def _stack(self, records, well: Well) -> Well:
        # TODO: Deal with Lithology, LtsaOwner, AquiferWell etc.
        # There isn't always a like to like mapping of values, sometimes the source key will differ from
        # the target key:
        activity_type_map = {
            WellActivityCode.types.construction().code: {
                'work_start_date': 'construction_start_date',
                'work_end_date': 'construction_end_date'
            },
            WellActivityCode.types.alteration().code: {
                'work_start_date': 'alteration_start_date',
                'work_end_date': 'alteration_end_date'
            },
            WellActivityCode.types.decommission().code: {
                'work_start_date': 'decommission_start_date',
                'work_end_date': 'decommission_end_date'
            }
        }

        # It's helpful for debugging, to limit the fields we consider only to target keys, for example
        # there are some values that don't actually map from the submission to the well (e.g. create_date,
        # filing number, well_activity_code etc.)
        target_keys = WellStackerSerializer().get_fields().keys()

        # Iterate through all the submission records
        # We can't strictly order by the create date, we need to consider that construction/legacy well
        # submission have to go 1st - in the following order:
        # 1: legacy submissions
        #   1.1: reason: Scenario. There is an existing well, a construction submission comes in, we have
        #           to create a legacy submission to retain the wells information, and apply the
        #           construction on top of that.
        # 2: construction submissions
        #   2.1: reason: A well should ideally always start with a construction submission. See 1.1 for
        #           the exception to this rule.
        # 3: create_date
        #   3.1 reason: Submissions need to be considered in order.
        #   3.2 exceptions: It may be, that two alterations are capture in the incorrect order. Logically,
        #           the record dated earlier by the "work_start_date" should be considered 1st, and should
        #           be captured 1st. We do however not have control over the order in which records are
        #           captured. WE CURRENTLY DO NOT HANDLE THIS EXCEPTION. It is important that and EDIT be
        #           processed ONLY based on it's create_date, not it's work_start_date.
        records = records.order_by('create_date')
        records = sorted(records, key=lambda record:
                         (record.well_activity_type.code != WellActivityCode.types.legacy().code,
                          record.well_activity_type.code != WellActivityCode.types.construction().code,
                          record.create_date))

        # these are depth-specific sets that have a "start" and "end" value
        FOREIGN_KEYS = ('casing_set', 'screen_set', 'linerperforation_set', 'decommission_description_set',)

        composite = {}

        # Well status is set based on the most recent activity submission.
        well_status_map = {
            WellActivityCode.types.construction().code: WellStatusCode.types.construction().well_status_code,
            WellActivityCode.types.alteration().code: WellStatusCode.types.alteration().well_status_code,
            WellActivityCode.types.decommission().code: WellStatusCode.types.decommission().well_status_code,
        }

        for submission in records:
            # add a well_status based on the current activity submission
            # a staff edit could still override this with a different value.
            composite['well_status'] = well_status_map.get(
                submission.well_activity_type.code, WellStatusCode.types.other().well_status_code)
            source_target_map = activity_type_map.get(submission.well_activity_type.code, {})
            serializer = submissions.serializers.WellSubmissionStackerSerializer(submission)
            for source_key, value in serializer.data.items():
                # We only consider items with values, and keys that are in our target
                # an exception is STAFF_EDIT submissions (we need to be able to accept empty values)
                if value or value is False or value == 0:
                    target_key = source_target_map.get(source_key, source_key)
                    if target_key in target_keys:
                        # The composite dict is built up by applying the set of submissions/edits in order.
                        #
                        # There are several cases for handling values:
                        #
                        # The first cases involve related foreign key sets (other tables that
                        # have records that reference the current submission/well). These are handled
                        # differently for staff edits (can replace the entire previous set), or for
                        # sets that reference a depth along the drilled well (must be merged checking for
                        # overlap).
                        #
                        # If the target_key is not in one of the foreign key sets (i.e., it's a property/
                        # column of a well), then the value can overwrite the previous composite value.
                        if (submission.well_activity_type.code == WellActivityCode.types.staff_edit().code and
                                target_key in composite and
                                (target_key in FOREIGN_KEYS)):
                            # staff edits come in with the entire set of values and thus can replace
                            # the composite value
                            composite[target_key] = value
                        elif target_key in composite and target_key in FOREIGN_KEYS:
                            # foreign key sets are based on depth and need special merge handling.
                            composite[target_key] = self._merge_series(composite[source_key], value)
                        else:
                            composite[target_key] = value

            composite['update_user'] = submission.create_user or composite['update_user']

        # Update the well view
        well_serializer = WellStackerSerializer(well, data=composite, partial=True)
        if well_serializer.is_valid(raise_exception=True):
            with reversion.create_revision():
                well = well_serializer.save()

        return well

    @transaction.atomic
    def _update_well_record(self, submission: ActivitySubmission) -> Well:
        """
        Used to update an existing well record.
        """
        records = ActivitySubmission.objects.filter(well=submission.well)
        if records.count() > 1:
            # If there's more than one submission we don't need to create a legacy well, we can safely
            # assume that the 1st submission is either a legacy or construction report submission.
            return self._stack(records, submission.well)
        else:
            # If there aren't prior submissions, we may create a legacy record using the current well
            # record.
            # Edge case of note:
            # Re. discussion with Lindsay on Oct 15 2018: There may be an instance, where there is a
            # pre-existing well, and a construct report is submitted. In this instance, we may end up with a
            # LEGACY record and a CONSTRUCTION record. This is odd, but we don't want to lose the information
            # stored in the existing well record. It is imerative that we always create a legacy record.
            self._create_legacy_submission(submission.well)
            # We should now have multiple records
            records = ActivitySubmission.objects.filter(well=submission.well)
            return self._stack(records, submission.well)
