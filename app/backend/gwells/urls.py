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
import os

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from gwells.views import SurveyListView
from gwells.views import HealthView
from gwells.views import HomeView
from gwells.views.admin import *
from gwells.views import api
from gwells.settings.base import get_env_variable

# Creating 2 versions of the app_root. One without and one with trailing slash
# This will allow for any or no additional app_root context to be provided
app_root = settings.APP_CONTEXT_ROOT
if app_root:
    app_root_slash = app_root + '/'
else:
    app_root_slash = app_root

DJANGO_ADMIN_URL = get_env_variable(
    'DJANGO_ADMIN_URL',
    # safe value used for development when DJANGO_ADMIN_URL might not be set
    'admin',
    strict=True
)


urlpatterns = [
    url(r'^' + app_root_slash, include('submissions.urls')),

    url(r'^' + app_root_slash + 'robots\.txt$',
        TemplateView.as_view(template_name='robots.txt',
                             content_type='text/plain'),
        name='robots'),


    url(r'^' + app_root_slash + 'health$', HealthView.health, name='health'),
    url(r'^' +
        app_root_slash +
        'site_admin/survey/(?P<pk>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        SurveyView.as_view(), name='survey'),  # survey details view
    url(r'^' + app_root_slash + 'site_admin/survey',
        SurveyView.as_view(), name='survey'),  # survey api view
    url(r'^' + app_root_slash + 'site_admin',
        AdminView.as_view(),
        name='site_admin'),  # editable list view of surveys and other site admin features

    # API routes
    url(r'^' + app_root_slash + 'api/v1/surveys$',
        SurveyListView.as_view(), name='survey-list'),
    url(r'^' + app_root_slash + DJANGO_ADMIN_URL + '/', admin.site.urls),
    url(r'^' + app_root_slash + 'accounts/',
        include('django.contrib.auth.urls')),
    url(r'^' + app_root_slash + 'api/v1/keycloak$',
        api.KeycloakConfig.as_view(), name='keycloak'),
    url(r'^' + app_root_slash + 'api/v1/config',
        api.GeneralConfig.as_view(), name='configuration'),
    url(r'^' + app_root_slash + 'api/v1/gis/insidebc',
        api.InsideBC.as_view(), name='insidebc'),
    url(r'^' + app_root_slash, include('registries.urls')),
    url(r'^' + app_root_slash, include('wells.urls')),
    url(r'^' + app_root_slash, include('aquifers.urls')),

    # main web application page
    url(r'^' + app_root_slash, HomeView.as_view(), name='home'),

]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
