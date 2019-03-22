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

from continuing_education.api.views.address import AddressDetailUpdateDestroy, AddressListCreate
from continuing_education.api.views.admission import AdmissionListCreate, AdmissionDetailUpdateDestroy
from continuing_education.api.views.continuing_education_person import ContinuingEducationPersonListCreate, \
    ContinuingEducationPersonDetailDestroy
from continuing_education.api.views.continuing_education_training import ContinuingEducationTrainingListCreate, \
    ContinuingEducationTrainingDetailUpdateDestroy
from continuing_education.api.views.file import AdmissionFileRetrieveDestroy, AdmissionFileListCreate
from continuing_education.api.views.prospect import ProspectListCreate, ProspectDetailUpdateDestroy
from continuing_education.api.views.registration import RegistrationList, RegistrationDetailUpdateDestroy

urlpatterns = [
    url(r'^addresses/$', AddressListCreate.as_view(), name=AddressListCreate.name),
    url(
        r'^addresses/(?P<uuid>[0-9a-f-]+)$',
        AddressDetailUpdateDestroy.as_view(),
        name=AddressDetailUpdateDestroy.name
    ),
    url(r'^persons/$', ContinuingEducationPersonListCreate.as_view(), name=ContinuingEducationPersonListCreate.name),
    url(
        r'^persons/(?P<uuid>[0-9a-f-]+)$',
        ContinuingEducationPersonDetailDestroy.as_view(),
        name=ContinuingEducationPersonDetailDestroy.name
    ),
    url(r'^persons/(?P<uuid>[0-9a-f-]+)/admissions/$', AdmissionListCreate.as_view(), name=AdmissionListCreate.name),
    url(
        r'^persons/(?P<uuid>[0-9a-f-]+)/admissions/(?P<admission_uuid>[0-9a-f-]+)$',
        AdmissionDetailUpdateDestroy.as_view(),
        name=AdmissionDetailUpdateDestroy.name
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
        r'^persons/(?P<uuid>[0-9a-f-]+)/registrations/(?P<registration_uuid>[0-9a-f-]+)$',
        RegistrationDetailUpdateDestroy.as_view(),
        name=RegistrationDetailUpdateDestroy.name
    ),
    url(r'^prospects/$', ProspectListCreate.as_view(), name=ProspectListCreate.name),
    url(
        r'^prospects/(?P<uuid>[0-9a-f-]+)$',
        ProspectDetailUpdateDestroy.as_view(),
        name=ProspectDetailUpdateDestroy.name
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
]
