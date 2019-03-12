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
from urllib.parse import quote

from django.db.models import Prefetch
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.contrib.gis.geos import Polygon

from django_filters import rest_framework as restfilters
from rest_framework_gis.filters import InBBoxFilter

from functools import reduce
import operator

from django.db.models import Q

from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from django_filters import rest_framework as restfilters

from minio import Minio

from gwells import settings
from gwells.documents import MinioClient
from gwells.models import Survey
from gwells.roles import WELLS_VIEWER_ROLE, WELLS_EDIT_ROLE
from gwells.pagination import APILimitOffsetPagination
from gwells.settings.base import get_env_variable

from wells.filters import WellListFilter
from wells.models import Well
from wells.serializers import (
    WellListSerializer,
    WellTagSearchSerializer,
    WellDetailSerializer,
    WellDetailAdminSerializer,
    WellLocationSerializer)
from wells.permissions import WellsEditPermissions, WellsEditOrReadOnly


class WellSearchFilter(restfilters.FilterSet):
    well_tag_number = restfilters.CharFilter()
    identification_plate_number = restfilters.CharFilter()
    owner_full_name = restfilters.CharFilter(lookup_expr='icontains')
    street_address = restfilters.CharFilter(lookup_expr='icontains')
    legal_plan = restfilters.CharFilter()
    legal_lot = restfilters.CharFilter()


class WellDetailView(DetailView):
    model = Well
    context_object_name = 'well'
    template_name = 'wells/well_detail.html'

    def get_context_data(self, **kwargs):
        """
        Return the context for the well details page.
        """

        context = super(WellDetailView, self).get_context_data(**kwargs)
        surveys = Survey.objects.order_by('create_date')
        context['surveys'] = surveys
        context['page'] = 'w'

        return context


class WellDetail(RetrieveAPIView):
    """
    Return well detail.
    This view is open to all, and has no permissions.
    """
    serializer_class = WellDetailSerializer

    # TODO Address viewing unpublished wells when advanced search has been merged
    queryset = Well.objects.all()  # exclude(well_publication_status='Unpublished')
    lookup_field = 'well_tag_number'

    def get_serializer(self, *args, **kwargs):
        """ returns a different serializer for admin users """

        serializer = self.serializer_class

        if (self.request.user and self.request.user.is_authenticated and
                self.request.user.groups.filter(name=WELLS_VIEWER_ROLE).exists()):
            serializer = WellDetailAdminSerializer
        return serializer(*args, **kwargs)


class ListExtracts(APIView):
    """
    List well extracts

    get: list well extracts
    """
    @swagger_auto_schema(auto_schema=None)
    def get(self, request):
        host = get_env_variable('S3_HOST')
        use_secure = int(get_env_variable('S3_USE_SECURE', 1))
        minioClient = Minio(host,
                            access_key=get_env_variable('S3_PUBLIC_ACCESS_KEY'),
                            secret_key=get_env_variable('S3_PUBLIC_SECRET_KEY'),
                            secure=use_secure)
        objects = minioClient.list_objects(get_env_variable('S3_WELL_EXPORT_BUCKET'))
        urls = list(
            map(
                lambda document: {
                    'url': 'https://{}/{}/{}'.format(host,
                                                     quote(document.bucket_name),
                                                     quote(document.object_name)),
                    'name': document.object_name,
                    'size': document.size,
                    'last_modified': document.last_modified,
                    'description': self.create_description(document.object_name)
                }, objects)
        )
        return Response(urls)

    def create_description(self, name):
        extension = name[name.rfind('.')+1:]
        if extension == 'zip':
            return 'ZIP, CSV'
        elif extension == 'xlsx':
            return 'XLSX'
        else:
            return None


class ListFiles(APIView):
    """
    List documents associated with a well (e.g. well construction report)

    get: list files found for the well identified in the uri
    """

    @swagger_auto_schema(responses={200: openapi.Response('OK',
        openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'public': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'url': openapi.Schema(type=openapi.TYPE_STRING),
                    'name': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )),
            'private': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'url': openapi.Schema(type=openapi.TYPE_STRING),
                    'name': openapi.Schema(type=openapi.TYPE_STRING)
                }
            ))
        })
    )})
    def get(self, request, tag):
        user_is_staff = self.request.user.groups.filter(
            name=WELLS_VIEWER_ROLE).exists()

        client = MinioClient(
            request=request, disable_private=(not user_is_staff))

        documents = client.get_documents(
            int(tag), resource="well", include_private=user_is_staff)

        return Response(documents)


class WellListAPIView(ListAPIView):
    """List and create wells

    get: returns a list of wells
    """

    permission_classes = (WellsEditOrReadOnly,)
    model = Well
    # TODO Address viewing unpublished wells when advanced search has been merged
    queryset = Well.objects.all()  # exclude(well_publication_status='Unpublished')
    pagination_class = APILimitOffsetPagination
    serializer_class = WellListSerializer
    bbox_filter_field = 'geom'
    filter_backends = (restfilters.DjangoFilterBackend, InBBoxFilter,
                       filters.SearchFilter, filters.OrderingFilter)
    ordering = ('well_tag_number',)
    filterset_class = WellListFilter
    search_fields = ('well_tag_number', 'identification_plate_number',
                     'street_address', 'city', 'owner_full_name')

    def get_queryset(self):
        qs = self.queryset
        qs = qs \
            .select_related(
                "bcgs_id",
            ).prefetch_related(
                Prefetch("water_quality_characteristics")
            ) \
            .order_by("well_tag_number")

        well_tag_or_plate = self.request.query_params.get('well', None)
        if well_tag_or_plate:
            qs = qs.filter(Q(well_tag_number=well_tag_or_plate) | Q(identification_plate_number=well_tag_or_plate))

        return qs

    def list(self, request):
        """ List wells with pagination """
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(filtered_queryset)
        if page is not None:
            serializer = WellListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = WellListSerializer(filtered_queryset, many=True)
        return Response(serializer.data)


class WellTagSearchAPIView(ListAPIView):
    """ seach for wells by tag or owner """

    permission_classes = (WellsEditOrReadOnly,)
    model = Well
    queryset = Well.objects.exclude(well_publication_status='Unpublished').only('well_tag_number', 'owner_full_name')
    pagination_class = None
    serializer_class = WellTagSearchSerializer
    lookup_field = 'well_tag_number'

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('well_tag_number',)
    search_fields = (
        'well_tag_number',
        'owner_full_name',
    )


class WellLocationListAPIView(ListAPIView):
    """ returns well locations for a given search

        get: returns a list of wells with locations only
    """

    permission_classes = (WellsEditOrReadOnly,)
    model = Well
    queryset = Well.objects.all()
    serializer_class = WellLocationSerializer

    # Allow searching on name fields, names of related companies, etc.
    filter_backends = (restfilters.DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter)
    ordering = ('well_tag_number',)
    filterset_class = WellSearchFilter
    pagination_class = None


    # search_fields and get_queryset are fragile here.
    # they need to match up with the search results returned by WellListAPIView.
    # an attempt was made to factor out filtering logic into WellSearchFilter (which WellLocationFilter inherits),
    # but so far, not all the searchable fields have been put into that class.
    # Please note the difference between "searchable fields" (one query param will return results that are valid
    # for any of these fields) and "filter fields" (search by a single individual fields)
    search_fields = ('legal_pid', 'legal_plan', 'legal_district_lot', 'legal_block', 'legal_section', 'legal_township', 'legal_range')

    def get_queryset(self):
        qs = self.queryset

        well_tag_or_plate = self.request.query_params.get('well', None)
        if well_tag_or_plate:
            qs = qs.filter(Q(well_tag_number=well_tag_or_plate) | Q(identification_plate_number=well_tag_or_plate))

        return qs

    def get(self, request):
        """ cancels request if too many wells are found"""
        bbox = (request.GET['sw_long'], request.GET['sw_lat'], request.GET['ne_long'], request.GET['ne_lat'])
        poly = Polygon.from_bbox(bbox)
        queryset = Well.objects.filter(geom__within=poly)
        count = WellSearchFilter(request.GET, queryset).qs.count()

        # return an empty response if there are too many wells to display
        if count > 2000:
            return Response([])
        return super().get(request)


class PreSignedDocumentKey(APIView):
    """
    Get a pre-signed document key to upload into an S3 compatible document store

    post: obtain a URL that is pre-signed to allow client-side uploads
    """

    queryset = Well.objects.all()
    permission_classes = (WellsEditPermissions,)

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, tag):
        well = get_object_or_404(self.queryset, pk=tag)
        client = MinioClient(
            request=request, disable_private=False)

        object_name = request.GET.get("filename")
        filename = client.format_object_name(object_name, int(well.well_tag_number), "well")
        bucket_name = get_env_variable("S3_ROOT_BUCKET")

        is_private = False
        if request.GET.get("private") == "true":
            is_private = True
            bucket_name = get_env_variable("S3_PRIVATE_ROOT_BUCKET")

        # TODO: This should probably be "S3_WELL_BUCKET" but that will require a file migration
        url = client.get_presigned_put_url(
            filename, bucket_name=bucket_name, private=is_private)

        return JsonResponse({"object_name": object_name, "url": url})


class DeleteWellDocument(APIView):
    """
    Delete a document from a S3 compatible store

    delete: remove the specified object from the S3 store
    """

    queryset = Well.objects.all()
    permission_classes = (WellsEditPermissions,)

    @swagger_auto_schema(auto_schema=None)
    def delete(self, request, tag):
        well = get_object_or_404(self.queryset, pk=tag)
        client = MinioClient(
            request=request, disable_private=False)

        is_private = False
        bucket_name = get_env_variable("S3_ROOT_BUCKET")

        if request.GET.get("private") == "true":
            is_private = True
            bucket_name = get_env_variable("S3_PRIVATE_ROOT_BUCKET")

        object_name = client.get_bucket_folder(int(well.well_tag_number), "well") + "/" + request.GET.get("filename")

        # TODO: This should probably be "S3_WELL_BUCKET" but that will require a file migration
        client.delete_document(object_name, bucket_name=bucket_name, private=is_private)

        return HttpResponse(status=204)
