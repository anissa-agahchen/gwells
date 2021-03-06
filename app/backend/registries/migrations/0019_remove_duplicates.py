# Generated by Django 2.1.8 on 2019-04-10 21:31
import logging

from django.utils import timezone
from django.db import transaction
from django.db import migrations

from gwells.models import DE_DUPLICATE_USER


logger = logging.getLogger(__name__)


def get_base_query(Organization, exclude):
    """
    We always filter on non-expired records, order by date, excluding organisations we've already processed.
    """
    # Only get non-expired records.
    query = Organization.objects.filter(effective_date__lt=timezone.now(), expiry_date__gt=timezone.now())
    # Put the most recent at the top.
    query = query.order_by('create_date', 'update_date')
    # Exclude organisations we've already processed.
    query = query.exclude(org_guid__in=exclude)
    return query


def get_duplicate_query(Organization, org, exclude, exact):
    """
    If we're doing an exact match, we make sure that all fields match.
    If we're not doing an exact match, we only match name, street_addres, city, province and postal code.
    """
    query = get_base_query(Organization, exclude)

    query = query.exclude(org_guid=org.org_guid)
    query = query.extra(where=['TRIM(name) = \'{}\''.format(org.name.replace('\'', '\'\'').strip())])
    query = query.filter(street_address=org.street_address)
    query = query.filter(city=org.city)
    query = query.filter(province_state=org.province_state)
    query = query.filter(postal_code=org.postal_code)
    if exact:
        query = query.filter(main_tel=org.main_tel)
        query = query.filter(fax_tel=org.fax_tel)
        query = query.filter(website_url=org.website_url)
        query = query.filter(email=org.email)
    return query


def can_expire(exact, duplicate):
    """
    We have different rules for when we can expire an organization.
    1. If we're doing an exact match, we can safely expire.
    2. If we're not doing an exact match, we only expire if there are no notes/registrations.
    """

    # By default we don't expire.
    expire = False
    if exact:
        # We can safely expire exact matches.
        expire = True
    else:
        if len(duplicate.registrations.all()) == 0 and len(duplicate.notes.all()) == 0:
            # No registrations? No notes? We can safely expire you!
            expire = True
        else:
            # Cannot safely expire, there's stuff attached to this guy.
            logger.info(('Cannot safely expire {duplicate.name} : {duplicate.org_guid} ; notes: {notes}, '
                         'registrations: {registrations}').format(
                            duplicate=duplicate,
                            registrations=len(duplicate.registrations.all()),
                            notes=len(duplicate.notes.all())))
    return expire


def expire_duplicates(Organization, exact=True, trial_run=True):
    """
    Expire duplicate organisations.
    """
    # Keep track of records to exclude as they're processed.
    exclude = []
    restart = True
    while restart:
        restart = False
        # Only get non-expired records.
        base_query = get_base_query(Organization, exclude)

        for org in base_query:
            # Add this organization to our exclusion list going forward.
            exclude.append(org.org_guid)
            # Get duplicates of this organization.
            duplicates = get_duplicate_query(Organization, org, exclude, exact)
            # If there are duplicates, let's consider removing them!
            if len(duplicates) > 0:
                with transaction.atomic():
                    for duplicate in duplicates:
                        expire = can_expire(exact, duplicate)
                        if expire:
                            # Get users associated with this org, and attach it to our new master.
                            for registration in duplicate.registrations.all():
                                logger.info(('Moving {registration} from {registration.organization} to '
                                             '{target}').format(registration=registration,
                                                                target=org))
                                registration.organization = org
                                registration.update_date = timezone.now()
                                registration.update_user = DE_DUPLICATE_USER
                                if not trial_run:
                                    registration.save()
                            # Get the notes associated with this org, and attach it to our new master.
                            for note in duplicate.notes.all():
                                logger.info('Moving {note} from {note.organization} to {target}'.format(
                                    note=note, target=org))
                                note.organization = org
                                note.update_date = timezone.now()
                                note.update_user = DE_DUPLICATE_USER
                                if not trial_run:
                                    note.save()
                            logger.info('Expiring {organization.name} ({organization.org_guid})'.format(
                                organization=duplicate
                            ))
                            duplicate.expiry_date = timezone.now()
                            duplicate.update_date = timezone.now()
                            duplicate.update_user = DE_DUPLICATE_USER
                            if not trial_run:
                                duplicate.save()
                        # Exclude this duplicate from future consideration.
                        exclude.append(duplicate.org_guid)
                # We need to re-run our base query, so we break and restart.
                restart = True
                break


# DON'T SQUASH
# There's no point squashing this - if you do a squash, just delete this - once this has
# been run in production, there's no point to it's continued existence.
def remove_duplicates(apps, schema_editor):
    Organization = apps.get_model('registries', 'Organization')
    # Expire exact matches.
    expire_duplicates(Organization, exact=True, trial_run=False)
    # Expire matches that aren't exact (slightly different rules apply)
    expire_duplicates(Organization, exact=False, trial_run=False)


def revert_remove_duplicates(apps, schema_editor):
    # There's no way to undo this!
    logger.info('Skipping revert')


class Migration(migrations.Migration):

    dependencies = [
        ('registries', '0018_auto_20190409_1634'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_duplicates,
            reverse_code=revert_remove_duplicates,
        ),
    ]
