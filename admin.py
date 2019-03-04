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

from django.contrib import admin

from continuing_education.models import *
from continuing_education.models import file

admin.site.register(
    admission.Admission,
    admission.AdmissionAdmin
)
admin.site.register(
    continuing_education_person.ContinuingEducationPerson,
    continuing_education_person.ContinuingEducationPersonAdmin
)
admin.site.register(
    address.Address,
    address.AddressAdmin
)
admin.site.register(
    file.AdmissionFile,
    file.AdmissionFileAdmin
)
admin.site.register(
    prospect.Prospect,
    prospect.ProspectAdmin
)
admin.site.register(
    continuing_education_training.ContinuingEducationTraining,
    continuing_education_training.ContinuingEducationTrainingAdmin
)
admin.site.register(
    person_training.PersonTraining,
    person_training.PersonTrainingAdmin
)
