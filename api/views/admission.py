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
from rest_framework import generics

from continuing_education.api.serializers.admission import AdmissionSerializer
from continuing_education.models.admission import Admission


class AdmissionList(generics.ListAPIView):
    """
       Return a list of all the training with optional filtering.
    """
    name = 'admission-list'
    queryset = Admission.objects.all().select_related(
        'person_information',
        'citizenship',
        'address',
        'billing_address',
        'residence_address'
    )
    serializer_class = AdmissionSerializer
    filter_fields = (
        'person_information',
        'formation',
        'state',
    )
    search_fields = (
        'person_information',
        'formation',
        'state',
    )
    ordering_fields = (
        'person_information',
        'formation',
        'state',
    )
    ordering = (
        'state',
        'formation',
    )  # Default ordering
