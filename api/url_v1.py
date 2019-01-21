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

from continuing_education.api.views.address import AddressDetail, AddressListCreate
from continuing_education.api.views.admission import AdmissionList, AdmissionDetail
from continuing_education.api.views.continuing_education_person import ContinuingEducationPersonDetail, \
    ContinuingEducationPersonListCreate
from continuing_education.api.views.file import AdmissionFileRetrieveDestroy, AdmissionFileListCreate

urlpatterns = [
    url(r'^addresses/$', AddressListCreate.as_view(), name=AddressListCreate.name),
    url(r'^addresses/(?P<uuid>[0-9a-f-]+)$', AddressDetail.as_view(), name=AddressDetail.name),
    url(r'^persons/$', ContinuingEducationPersonListCreate.as_view(), name=ContinuingEducationPersonListCreate.name),
    url(
        r'^persons/(?P<uuid>[0-9a-f-]+)$',
        ContinuingEducationPersonDetail.as_view(),
        name=ContinuingEducationPersonDetail.name
    ),
    url(r'^admissions/$', AdmissionList.as_view(), name=AdmissionList.name),
    url(r'^admissions/(?P<uuid>[0-9a-f-]+)$', AdmissionDetail.as_view(), name=AdmissionDetail.name),
    url(r'^admissions/(?P<uuid>[0-9a-f-]+)/files/$', AdmissionFileListCreate.as_view(), name=AdmissionFileListCreate.name),
    url(
        r'^admissions/(?P<uuid>[0-9a-f-]+)/files/(?P<file_uuid>[0-9a-f-]+)$',
        AdmissionFileRetrieveDestroy.as_view(),
        name=AdmissionFileRetrieveDestroy.name
    ),

]
