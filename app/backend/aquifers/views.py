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
from datetime import datetime
import logging

from django_filters import rest_framework as djfilters
from django.http import Http404, HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.db import connection

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny

from reversion.views import RevisionMixin

from gwells.documents import MinioClient
from gwells.roles import AQUIFERS_EDIT_ROLE
from gwells.settings.base import get_env_variable

from aquifers import models
from aquifers import serializers
from aquifers.models import (
    Aquifer,
    AquiferDemand,
    AquiferMaterial,
    AquiferProductivity,
    AquiferSubtype,
    AquiferVulnerabilityCode,
)
from aquifers.permissions import HasAquiferEditRoleOrReadOnly, HasAquiferEditRole
from gwells.change_history import generate_history_diff
from registries.views import AuditCreateMixin, AuditUpdateMixin


logger = logging.getLogger(__name__)


class AquiferRetrieveUpdateAPIView(RevisionMixin, AuditUpdateMixin, RetrieveUpdateAPIView):
    """List aquifers
    get: return details of aquifers
    patch: update aquifer
    """

    permission_classes = (HasAquiferEditRoleOrReadOnly,)
    queryset = Aquifer.objects.all()
    lookup_field = 'aquifer_id'
    serializer_class = serializers.AquiferSerializer


class AquiferListCreateAPIView(RevisionMixin, AuditCreateMixin, ListCreateAPIView):
    """List aquifers
    get: return a list of aquifers
    post: create an aquifer
    """

    permission_classes = (HasAquiferEditRoleOrReadOnly,)
    queryset = Aquifer.objects.all()
    serializer_class = serializers.AquiferSerializer
    filter_backends = (djfilters.DjangoFilterBackend,
                       OrderingFilter, SearchFilter)
    filter_fields = ('aquifer_id',)
    search_fields = ('aquifer_name',)
    ordering_fields = '__all__'
    ordering = ('aquifer_id',)


class AquiferMaterialListAPIView(ListAPIView):
    """List aquifer materials codes
    get: return a list of aquifer material codes
    """

    queryset = AquiferMaterial.objects.all()
    serializer_class = serializers.AquiferMaterialSerializer


class QualityConcernListAPIView(ListAPIView):
    """List aquifer materials codes
    get: return a list of quality concern codes
    """

    queryset = models.QualityConcern.objects.all()
    serializer_class = serializers.QualityConcernSerializer


class AquiferVulnerabilityListAPIView(ListAPIView):
    """List aquifer vulnerability codes
    get: return a list of aquifer vulnerability codes
    """

    queryset = AquiferVulnerabilityCode.objects.all()
    serializer_class = serializers.AquiferVulnerabilitySerializer


class AquiferSubtypeListAPIView(ListAPIView):
    """List aquifer subtypes codes
    get: return a list of aquifer subtype codes
    """

    queryset = AquiferSubtype.objects.all()
    serializer_class = serializers.AquiferSubtypeSerializer


class AquiferProductivityListAPIView(ListAPIView):
    """List aquifer productivity codes
    get: return a list of aquifer productivity codes
    """

    queryset = AquiferProductivity.objects.all()
    serializer_class = serializers.AquiferProductivitySerializer


class AquiferDemandListAPIView(ListAPIView):
    """List aquifer demand codes
    get: return a list of aquifer demand codes
    """

    queryset = AquiferDemand.objects.all()
    serializer_class = serializers.AquiferDemandSerializer


class WaterUseListAPIView(ListAPIView):
    """List Water Use Codes
    get: return a list of water use codes
    """

    queryset = models.WaterUse.objects.all()
    serializer_class = serializers.WaterUseSerializer


class ListFiles(APIView):
    """
    List documents associated with an aquifer

    get: list files found for the aquifer identified in the uri
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
    def get(self, request, aquifer_id):
        user_is_staff = self.request.user.groups.filter(
            name=AQUIFERS_EDIT_ROLE).exists()

        client = MinioClient(
            request=request, disable_private=(not user_is_staff))

        documents = client.get_documents(
            int(aquifer_id), resource="aquifer", include_private=user_is_staff)

        return Response(documents)


class AquiferNameList(ListAPIView):
    """ List all aquifers in a simplified format """

    serializer_class = serializers.AquiferSerializerBasic
    model = Aquifer
    queryset = Aquifer.objects.all()
    pagination_class = None

    filter_backends = (filters.SearchFilter,)
    ordering = ('aquifer_id',)
    search_fields = (
        'aquifer_id',
        'aquifer_name',
    )

    def get(self, request):
        search = self.request.query_params.get('search', None)
        if not search or len(search) < 3:
            # avoiding responding with excess results
            return Response([])
        else:
            return super().get(request)


class AquiferHistory(APIView):
    """
    get: returns a history of changes to a Aquifer model record
    """
    permission_classes = (HasAquiferEditRole,)
    queryset = Aquifer.objects.all()
    swagger_schema = None

    def get(self, request, aquifer_id):
        """
        Retrieves version history for the specified Aquifer record and creates a list of diffs
        for each revision.
        """

        try:
            aquifer = Aquifer.objects.get(aquifer_id=aquifer_id)
        except Aquifer.DoesNotExist:
            raise Http404("Aquifer not found")

        # query records in history for this model.
        aquifer_history = [obj for obj in aquifer.history.all().order_by(
            '-revision__date_created')]

        aquifer_history_diff = generate_history_diff(
            aquifer_history, 'aquifer ' + aquifer_id)

        history_diff = sorted(aquifer_history_diff, key=lambda x: x['date'], reverse=True)

        return Response(history_diff)


class PreSignedDocumentKey(APIView):
    """
    Get a pre-signed document key to upload into an S3 compatible document store

    post: obtain a URL that is pre-signed to allow client-side uploads
    """

    permission_classes = (HasAquiferEditRole,)

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, aquifer_id):
        client = MinioClient(
            request=request, disable_private=False)

        object_name = request.GET.get("filename")
        filename = client.format_object_name(object_name, int(aquifer_id), "aquifer")
        bucket_name = get_env_variable("S3_AQUIFER_BUCKET")

        is_private = False
        if request.GET.get("private") == "true":
            is_private = True
            bucket_name = get_env_variable("S3_PRIVATE_AQUIFER_BUCKET")

        url = client.get_presigned_put_url(
            filename, bucket_name=bucket_name, private=is_private)

        return JsonResponse({"object_name": object_name, "url": url})


class DeleteAquiferDocument(APIView):
    """
    Delete a document from a S3 compatible store

    delete: remove the specified object from the S3 store
    """

    permission_classes = (HasAquiferEditRole,)

    @swagger_auto_schema(auto_schema=None)
    def delete(self, request, aquifer_id):
        client = MinioClient(
            request=request, disable_private=False)

        is_private = False
        bucket_name = get_env_variable("S3_AQUIFER_BUCKET")

        if request.GET.get("private") == "true":
            is_private = True
            bucket_name = get_env_variable("S3_PRIVATE_AQUIFER_BUCKET")

        object_name = client.get_bucket_folder(int(aquifer_id), "aquifer") + "/" + request.GET.get("filename")
        client.delete_document(object_name, bucket_name=bucket_name, private=is_private)

        return HttpResponse(status=204)


class AquifersSpatial(APIView):

    permission_classes = (AllowAny,)

    def get(self, request):
        sql = ("""
select row_to_json(fc)
from (
    select
        'FeatureCollection' as "type",
        array_to_json(array_agg(f)) as "features"
    from (
        select
            'Feature' as "type",
            ST_AsGeoJSON(geom) :: json as "geometry",
            (
                select json_strip_nulls(row_to_json(t))
                from (
                    select aquifer_id,
                    aquifer_name,
                    location_description,
                    aquifer_material_code.description as aquifer_material_description,
                    aquifer_subtype_code.description as aquifer_subtype_description,
                    area,
                    aquifer_vulnerability_code.description as aquifer_vulnerablity_description,
                    aquifer_productivity_code.description as aquifer_productivity_description,
                    aquifer_demand_code.description as aquifer_demand_description,
                    water_use_code.description as water_use_description,
                    quality_concern_code.description as quality_concern_description,
                    litho_stratographic_unit,
                    mapping_year,
                    notes
                ) t
            ) as properties
            from aquifer
                left join aquifer_material_code on
                    aquifer_material_code.aquifer_material_code = aquifer.aquifer_material_code
                left join aquifer_subtype_code on
                    aquifer_subtype_code.aquifer_subtype_code = aquifer.aquifer_subtype_code
                left join aquifer_vulnerability_code on
                    aquifer_vulnerability_code.aquifer_vulnerability_code = aquifer.aquifer_vulnerablity_code
                left join aquifer_productivity_code on
                    aquifer_productivity_code.aquifer_productivity_code = aquifer.aquifer_productivity_code
                left join aquifer_demand_code on
                    aquifer_demand_code.aquifer_demand_code = aquifer.aquifer_demand_code
                left join water_use_code on
                    water_use_code.water_use_code = aquifer.water_use_code
                left join quality_concern_code on
                    quality_concern_code.quality_concern_code = aquifer.quality_concern_code
    ) as f
) as fc;""")
        start = datetime.now()
        logger.info('fetching aquifer spatial data from database...')
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
            logger.info('aquifer spatial db query took: {}'.format(datetime.now() - start))
            return JsonResponse(row[0])
