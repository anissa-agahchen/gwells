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
from django.conf.urls import url
from django.views.decorators.cache import never_cache
from rest_framework.documentation import include_docs_urls
from rest_framework_jwt.views import obtain_jwt_token
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from registries import permissions
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Groundwater Wells, Aquifers and Registry API",
        default_version='v1',
        description=str("The groundwater wells, aquifers and registry API contains information "
                        "related to groundwater wells and aquifers as well as a register of qualified "
                        "well drillers and well pump installers registered to operate in B.C."),
        terms_of_service="http://www2.gov.bc.ca/gov/content?id=D1EE0A405E584363B205CD4353E02C88",
        contact=openapi.Contact(email="groundwater@gov.bc.ca"),
        license=openapi.License(name="Open Government License - British Columbia",
                                url="https://www2.gov.bc.ca/gov/content?id=A519A56BC2BF44E4A008B33FCF527F61"),
    ),
    public=False,
    permission_classes=(permissions.RegistriesEditOrReadOnly,)
)

urlpatterns = [

    # Organization note endpoints
    url(r'^api/v1/organizations/(?P<org_guid>[-\w]+)/notes$',
        views.OrganizationNoteListView.as_view(), name='org-note-list'),
    url(r'^api/v1/organizations/(?P<org_guid>[-\w]+)/notes/(?P<note_guid>[-\w]+)$',
        views.OrganizationNoteDetailView.as_view(), name='org-note-detail'),

    # Organization endpoints
    url(r'^api/v1/organizations/names$',
        never_cache(views.OrganizationNameListView.as_view()),
        name='organization-names'),
    url(r'^api/v1/organizations/(?P<org_guid>[-\w]+)/history$',
        never_cache(views.OrganizationHistory.as_view()), name='organization-history'),
    url(r'^api/v1/organizations/(?P<org_guid>[-\w]+)$',
        never_cache(views.OrganizationDetailView.as_view()),
        name='organization-detail'),
    url(r'^api/v1/organizations$',
        never_cache(views.OrganizationListView.as_view()),
        name='organization-list'),

    # Document Uploading (driller records)
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/presigned_put_url$',
        never_cache(views.PreSignedDocumentKey.as_view()), name='drillers-pre-signed-url'),

    # Document Deleting (driller records)
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/delete_document$',
        never_cache(views.DeleteDrillerDocument.as_view()), name='driller-delete-document'),

    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/files$',
        never_cache(views.ListFiles.as_view()), name='drillers-file-list'),

    # Person note endpoints
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/notes$',
        never_cache(views.PersonNoteListView.as_view()), name='person-note-list'),
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/notes/(?P<note_guid>[-\w]+)$',
        views.PersonNoteDetailView.as_view(), name='person-note-detail'),

    # Person endpoints (drillers, well installers, and other instances of Person model)
    # TODO: There's some confusion between drillers and persons. Sometimes we're looking only for drillers,
    # sometimes we're actually looking for people (pump installers, drillers etc.)
    url(r'^api/v1/drillers/names$',
        never_cache(views.PersonNameSearch.as_view()), name='person-search'),
    url(r'api/v1/drillers/options$',
        views.PersonOptionsView.as_view(), name='person-options'),
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)/history$',
        never_cache(views.PersonHistory.as_view()), name='person-history'),
    url(r'^api/v1/drillers/(?P<person_guid>[-\w]+)$',
        never_cache(views.PersonDetailView.as_view()),
        name='person-detail'),
    url(r'^api/v1/drillers$',
        never_cache(views.PersonListView.as_view()), name='person-list'),

    # Registration endpoints (a person may register as a driller or well pump installer)
    url(r'api/v1/registrations/(?P<register_guid>[-\w]+)$',
        never_cache(views.RegistrationDetailView.as_view()),
        name='register-detail'),
    url(r'api/v1/registrations$',
        never_cache(views.RegistrationListView.as_view()), name='register-list'),

    # Applications (applications to be qualified for a drilling activity)
    url(r'api/v1/applications/(?P<application_guid>[-\w]+)$',
        never_cache(views.ApplicationDetailView.as_view()),
        name='application-detail'),
    url(r'api/v1/applications$', never_cache(views.ApplicationListView.as_view()),
        name='application-list'),

    # List of cities that currently have registered drillers, pump installers etc.
    url(r'^api/v1/cities/drillers$',
        never_cache(views.CitiesListView.as_view()),
        {'activity': 'drill'},
        name='city-list-drillers'),
    url(r'^api/v1/cities/installers$',
        never_cache(views.CitiesListView.as_view()),
        {'activity': 'install'},
        name='city-list-installers'),

    # Swagger documentation endpoint
    url(r'^api/$', schema_view.with_ui('redoc',
                                       cache_timeout=None), name='api-docs'),

]
