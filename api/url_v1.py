##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from continuing_education.api.views.address import AddressDetailUpdate, AddressListCreate
from continuing_education.api.views.admission import AdmissionList, AdmissionDetailUpdate, AdmissionCreate
from continuing_education.api.views.continuing_education_person import ContinuingEducationPersonListCreate, \
    ContinuingEducationPersonDetail
from continuing_education.api.views.continuing_education_training import ContinuingEducationTrainingListCreate, \
    ContinuingEducationTrainingDetailUpdateDestroy
from continuing_education.api.views.file import AdmissionFileRetrieveDestroy, AdmissionFileListCreate
from continuing_education.api.views.prospect import ProspectListCreate, ProspectDetailUpdate
from continuing_education.api.views.registration import RegistrationList, RegistrationDetailUpdate, \
    RegistrationDetailForEpc, RegistrationListForEpc

# schema_view = get_swagger_view(title='IUFC API')
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # url(r'^$', schema_view),
    url(r'^addresses/$', AddressListCreate.as_view(), name=AddressListCreate.name),
    url(
        r'^addresses/(?P<uuid>[0-9a-f-]+)$',
        AddressDetailUpdate.as_view(),
        name=AddressDetailUpdate.name
    ),
    url(r'^persons/$', ContinuingEducationPersonListCreate.as_view(), name=ContinuingEducationPersonListCreate.name),
    url(
        r'^persons/details$',
        ContinuingEducationPersonDetail.as_view(),
        name=ContinuingEducationPersonDetail.name
    ),
    url(r'^persons/(?P<uuid>[0-9a-f-]+)/admissions/$', AdmissionList.as_view(), name=AdmissionList.name),
    url(
        r'^admissions/(?P<uuid>[0-9a-f-]+)$',
        AdmissionDetailUpdate.as_view(),
        name=AdmissionDetailUpdate.name
    ),
    url(
        r'^admissions/$',
        AdmissionCreate.as_view(),
        name=AdmissionCreate.name
    ),
    url(
        r'^admissions/(?P<uuid>[0-9a-f-]+)/files/$',
        AdmissionFileListCreate.as_view(),
        name=AdmissionFileListCreate.name
    ),
    url(
        r'^admissions/(?P<uuid>[0-9a-f-]+)/files/(?P<file_uuid>[0-9a-f-]+)$',
        AdmissionFileRetrieveDestroy.as_view(),
        name=AdmissionFileRetrieveDestroy.name
    ),
    url(r'^persons/(?P<uuid>[0-9a-f-]+)/registrations/$', RegistrationList.as_view(), name=RegistrationList.name),
    url(
        r'^registrations/(?P<uuid>[0-9a-f-]+)$',
        RegistrationDetailUpdate.as_view(),
        name=RegistrationDetailUpdate.name
    ),
    url(r'^prospects/$', ProspectListCreate.as_view(), name=ProspectListCreate.name),
    url(
        r'^prospects/(?P<uuid>[0-9a-f-]+)$',
        ProspectDetailUpdate.as_view(),
        name=ProspectDetailUpdate.name
    ),
    url(
        r'^training/$',
        ContinuingEducationTrainingListCreate.as_view(),
        name=ContinuingEducationTrainingListCreate.name
    ),
    url(
        r'^training/(?P<uuid>[0-9a-f-]+)$',
        ContinuingEducationTrainingDetailUpdateDestroy.as_view(),
        name=ContinuingEducationTrainingDetailUpdateDestroy.name
    ),
    url(r'^registration/for_epc/$', RegistrationListForEpc.as_view(),
        name=RegistrationListForEpc.name),
    url(r'^registration/for_epc/(?P<id>[0-9]+)/$', RegistrationDetailForEpc.as_view(),
        name=RegistrationDetailForEpc.name),
]
