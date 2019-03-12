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
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework_gis.filters import GeometryFilter

from wells.models import Well


class WellListFilter(filters.FilterSet):
    well = filters.CharFilter(method='filter_well_tag_or_plate',
                              label='Well tag or identification plate number')
    street_address_or_city = filters.CharFilter(method='filter_street_address_or_city',
                                                label='Street address or city')
    owner_full_name = filters.CharFilter(lookup_expr='icontains')
    legal = filters.CharFilter(method='filter_combined_legal',
                               label='Legal lot, District legal lot, Legal plan or Legal PID')
    date_of_work = filters.DateFromToRangeFilter(method='filter_date_of_work',
                                                 label='Date of work')
    well_depth = filters.RangeFilter(method='filter_well_depth',
                                     label='Well depth (finished or total)')

    street_address = filters.CharFilter(lookup_expr='icontains')
    city = filters.CharFilter(lookup_expr='icontains')
    well_location_description = filters.CharFilter(lookup_expr='icontains')
    construction_start_date = filters.DateFromToRangeFilter()
    construction_end_date = filters.DateFromToRangeFilter(label='Construction End Date')
    alteration_start_date = filters.DateFromToRangeFilter()
    alteration_end_date = filters.DateFromToRangeFilter(label='Alteration End Date')
    decommission_start_date = filters.DateFromToRangeFilter()
    decommission_end_date = filters.DateFromToRangeFilter()
    well_identification_plate_attached = filters.CharFilter(lookup_expr='icontains')
    water_supply_system_name = filters.CharFilter(lookup_expr='icontains')
    water_supply_system_well_name = filters.CharFilter(lookup_expr='icontains')
    geom = GeometryFilter()
    ground_elevation = filters.RangeFilter()
    surface_seal_length = filters.RangeFilter()
    surface_seal_thickness = filters.RangeFilter()
    surface_seal_depth = filters.RangeFilter()
    backfill_type = filters.CharFilter(lookup_expr='icontains')
    backfill_depth = filters.RangeFilter()
    liner_diameter = filters.RangeFilter()
    liner_thickness = filters.RangeFilter()
    liner_from = filters.RangeFilter()
    liner_to = filters.RangeFilter()
    other_screen_material = filters.CharFilter(lookup_expr='icontains')
    other_screen_bottom = filters.CharFilter(lookup_expr='icontains')
    screen_information = filters.CharFilter(lookup_expr='icontains')
    filter_pack_from = filters.RangeFilter()
    filter_pack_to = filters.RangeFilter()
    filter_pack_thickness = filters.RangeFilter()
    development_hours = filters.RangeFilter()
    development_notes = filters.CharFilter(lookup_expr='icontains')
    yield_estimation_rate = filters.RangeFilter()
    yield_estimation_duration = filters.RangeFilter()
    static_level_before_test = filters.RangeFilter()
    drawdown = filters.RangeFilter()
    hydro_fracturing_yield_increase = filters.RangeFilter()
    recommended_pump_depth = filters.RangeFilter()
    recommended_pump_rate = filters.RangeFilter()
    water_quality_colour = filters.CharFilter(lookup_expr='icontains')
    water_quality_odour = filters.CharFilter(lookup_expr='icontains')
    well_yield = filters.RangeFilter()
    observation_well_number = filters.CharFilter(lookup_expr='icontains')
    utm_northing = filters.RangeFilter()
    utm_easting = filters.RangeFilter()
    decommission_reason = filters.CharFilter(lookup_expr='icontains')
    decommission_sealant_material = filters.CharFilter(lookup_expr='icontains')
    decommission_backfill_material = filters.CharFilter(lookup_expr='icontains')
    decommission_details = filters.CharFilter(lookup_expr='icontains')
    aquifer_vulnerability_index = filters.RangeFilter()
    storativity = filters.RangeFilter()
    transmissivity = filters.RangeFilter()
    hydraulic_conductivity = filters.CharFilter(lookup_expr='icontains')
    specific_storage = filters.CharFilter(lookup_expr='icontains')
    specific_yield = filters.RangeFilter()
    testing_method = filters.CharFilter(lookup_expr='icontains')
    testing_duration = filters.RangeFilter()
    analytic_solution_type = filters.RangeFilter()
    boundary_effect = filters.RangeFilter()

    class Meta:
        model = Well
        fields = [
            'well',
            'well_tag_number',
            'identification_plate_number',
            'street_address_or_city',
            'street_address',
            'city',
            'owner_full_name',
            'legal',
            'legal_lot',
            'legal_plan',
            'legal_district_lot',
            'legal_pid',
            'land_district',
            'well_status',
            'licenced_status',
            'company_of_person_responsible',
            'person_responsible',
            'date_of_work',
            'well_depth',
            'aquifer',
            'well_class',
            'well_subclass',
            'legal_block',
            'legal_section',
            'legal_township',
            'legal_range',
            'well_location_description',
            'construction_start_date',
            'construction_end_date',
            'alteration_start_date',
            'alteration_end_date',
            'decommission_start_date',
            'decommission_end_date',
            'drilling_company',
            'well_identification_plate_attached',
            'id_plate_attached_by',
            'water_supply_system_name',
            'water_supply_system_well_name',
            'coordinate_acquisition_code',
            'ground_elevation',
            'ground_elevation_method',
            'drilling_methods',
            'well_orientation',
            'surface_seal_material',
            'surface_seal_length',
            'surface_seal_thickness',
            'surface_seal_method',
            'surface_seal_depth',
            'backfill_type',
            'backfill_depth',
            'liner_material',
            'liner_diameter',
            'liner_thickness',
            'liner_from',
            'liner_to',
            'screen_intake_method',
            'screen_type',
            'screen_material',
            'other_screen_material',
            'screen_opening',
            'screen_bottom',
            'other_screen_bottom',
            'screen_information',
            'filter_pack_from',
            'filter_pack_to',
            'filter_pack_thickness',
            'filter_pack_material',
            'filter_pack_material_size',
            'development_methods',
            'development_hours',
            'development_notes',
            'yield_estimation_method',
            'yield_estimation_rate',
            'yield_estimation_duration',
            'well_yield_unit',
            'static_level_before_test',
            'drawdown',
            'hydro_fracturing_performed',
            'hydro_fracturing_yield_increase',
            'recommended_pump_depth',
            'recommended_pump_rate',
            'water_quality_characteristics',
            'water_quality_colour',
            'water_quality_odour',
            'total_depth_drilled',
            'finished_well_depth',
            'well_yield',
            'diameter',
            'observation_well_number',
            'observation_well_status',
            'ems',
            'utm_zone_code',
            'utm_northing',
            'utm_easting',
            'bcgs_id',
            'decommission_reason',
            'decommission_method',
            'decommission_sealant_material',
            'decommission_backfill_material',
            'decommission_details',
            'aquifer_vulnerability_index',
            'storativity',
            'transmissivity',
            'hydraulic_conductivity',
            'specific_storage',
            'specific_yield',
            'testing_method',
            'testing_duration',
            'analytic_solution_type',
            'boundary_effect',
        ]

    def filter_well_tag_or_plate(self, queryset, name, value):
        return queryset.filter(Q(well_tag_number=value) |
                               Q(identification_plate_number=value))

    def filter_street_address_or_city(self, queryset, name, value):
        return queryset.filter(Q(street_address__icontains=value) |
                               Q(city__icontains=value))

    def filter_combined_legal(self, queryset, name, value):
        lookups = (
            Q(legal_lot=value) |
            Q(legal_plan=value) |
            Q(legal_district_lot=value)
        )
        # Check if we have a positive integer before querying the
        # legal_pid field.
        try:
            int_value = int(value)
        except (TypeError, ValueError):
            pass
        else:
            if int_value >= 0:
                lookups = lookups | Q(legal_pid=int_value)

        return queryset.filter(lookups)

    def filter_date_of_work(self, queryset, name, value):
        if value.start is not None and value.stop is not None:
            range_dates = (value.start.date(), value.stop.date())
            queryset = queryset.filter(
                Q(construction_start_date__range=range_dates) |
                Q(construction_end_date__range=range_dates) |
                Q(alteration_start_date__range=range_dates) |
                Q(alteration_end_date__range=range_dates) |
                Q(decommission_start_date__range=range_dates) |
                Q(decommission_end_date__range=range_dates)
            )
        elif value.start is not None:
            after_date = value.start.date()
            queryset = queryset.filter(
                Q(construction_start_date__gte=after_date) |
                Q(construction_end_date__gte=after_date) |
                Q(alteration_start_date__gte=after_date) |
                Q(alteration_end_date__gte=after_date) |
                Q(decommission_start_date__gte=after_date) |
                Q(decommission_end_date__gte=after_date)
            )
        elif value.stop is not None:
            before_date = value.stop.date()
            queryset = queryset.filter(
                Q(construction_start_date__lte=before_date) |
                Q(construction_end_date__lte=before_date) |
                Q(alteration_start_date__lte=before_date) |
                Q(alteration_end_date__lte=before_date) |
                Q(decommission_start_date__lte=before_date) |
                Q(decommission_end_date__lte=before_date)
            )

        return queryset

    def filter_well_depth(self, queryset, name, value):
        if value.start is not None and value.stop is not None:
            queryset = queryset.filter(
                Q(finished_well_depth__range=(value.start, value.stop)) |
                Q(total_depth_drilled__range=(value.start, value.stop))
            )
        elif value.start is not None:
            queryset = queryset.filter(
                Q(finished_well_depth__gte=value.start) |
                Q(total_depth_drilled__gte=value.start)
            )
        elif value.stop is not None:
            queryset = queryset.filter(
                Q(finished_well_depth__lte=value.stop) |
                Q(total_depth_drilled__lte=value.stop)
            )

        return queryset
