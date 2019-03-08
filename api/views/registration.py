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
from django_filters import rest_framework as filters
from rest_framework import generics

from continuing_education.api.serializers.registration import RegistrationListSerializer, \
    RegistrationDetailSerializer, RegistrationPostSerializer
from continuing_education.models.admission import Admission


class RegistrationFilter(filters.FilterSet):
    person = filters.CharFilter(field_name="person_information__person__uuid")

    class Meta:
        model = Admission
        fields = ['person_information', 'formation', 'state']


class RegistrationList(generics.ListAPIView):
    """
       Return a list of all the registration with optional filtering or create one.
    """
    name = 'registration-list'

    serializer_class = RegistrationListSerializer
    filter_class = RegistrationFilter

    search_fields = (
        'person_information',
        'formation',
        'state',
    )
    ordering_fields = (
        'person_information__person__last_name',
        'formation',
        'state',
    )
    ordering = (
        'state',
        'formation',
    )  # Default ordering

    def get_queryset(self):
        queryset = Admission.registration_objects.all().select_related(
            'person_information',
            'address',
            'billing_address',
            'residence_address'
        )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RegistrationPostSerializer
        return RegistrationListSerializer


class RegistrationDetailUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
        Return the detail of the registration, update or destroy it
    """
    name = 'registration-detail-update-destroy'
    queryset = Admission.objects.all()
    serializer_class = RegistrationDetailSerializer
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return RegistrationPostSerializer
        return RegistrationDetailSerializer
