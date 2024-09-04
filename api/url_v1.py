##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.urls import path, re_path

from continuing_education.api.views.address import AddressDetailUpdate, AddressListCreate
from continuing_education.api.views.admission import AdmissionList, AdmissionDetailUpdate, AdmissionCreate
from continuing_education.api.views.continuing_education_person import (
    ContinuingEducationPersonListCreate,
    ContinuingEducationPersonDetail,
)
from continuing_education.api.views.continuing_education_training import (
    ContinuingEducationTrainingListCreate,
    ContinuingEducationTrainingDetailUpdateDestroy,
)
from continuing_education.api.views.file import AdmissionFileRetrieveDestroy, AdmissionFileListCreate
from continuing_education.api.views.prospect import ProspectListCreate, ProspectDetailUpdate
from continuing_education.api.views.registration import RegistrationList, RegistrationDetailUpdate

app_name = "continuing_education"
urlpatterns = [
    path('addresses/', AddressListCreate.as_view(), name=AddressListCreate.name),
    re_path(
        r'^addresses/(?P<uuid>[0-9a-f-]+)$',
        AddressDetailUpdate.as_view(),
        name=AddressDetailUpdate.name
    ),
    path('persons/', ContinuingEducationPersonListCreate.as_view(), name=ContinuingEducationPersonListCreate.name),
    path('persons/details', ContinuingEducationPersonDetail.as_view(),
        name=ContinuingEducationPersonDetail.name
    ),
    re_path(r'^persons/(?P<uuid>[0-9a-f-]+)/admissions/$', AdmissionList.as_view(), name=AdmissionList.name),
    re_path(
        r'^admissions/(?P<uuid>[0-9a-f-]+)$',
        AdmissionDetailUpdate.as_view(),
        name=AdmissionDetailUpdate.name
    ),
    path('admissions/', AdmissionCreate.as_view(),
        name=AdmissionCreate.name
    ),
    re_path(
        r'^admissions/(?P<uuid>[0-9a-f-]+)/files/$',
        AdmissionFileListCreate.as_view(),
        name=AdmissionFileListCreate.name
    ),
    re_path(
        r'^admissions/(?P<uuid>[0-9a-f-]+)/files/(?P<file_uuid>[0-9a-f-]+)$',
        AdmissionFileRetrieveDestroy.as_view(),
        name=AdmissionFileRetrieveDestroy.name
    ),
    re_path(r'^persons/(?P<uuid>[0-9a-f-]+)/registrations/$', RegistrationList.as_view(), name=RegistrationList.name),
    re_path(
        r'^registrations/(?P<uuid>[0-9a-f-]+)$',
        RegistrationDetailUpdate.as_view(),
        name=RegistrationDetailUpdate.name
    ),
    path('prospects/', ProspectListCreate.as_view(), name=ProspectListCreate.name),
    re_path(
        r'^prospects/(?P<uuid>[0-9a-f-]+)$',
        ProspectDetailUpdate.as_view(),
        name=ProspectDetailUpdate.name
    ),
    path('training/', ContinuingEducationTrainingListCreate.as_view(),
        name=ContinuingEducationTrainingListCreate.name
    ),
    re_path(
        r'^training/(?P<uuid>[0-9a-f-]+)$',
        ContinuingEducationTrainingDetailUpdateDestroy.as_view(),
        name=ContinuingEducationTrainingDetailUpdateDestroy.name
    )
]
