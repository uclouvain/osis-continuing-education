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
from rest_framework.generics import get_object_or_404

from continuing_education.api.serializers.admission import AdmissionDetailSerializer, \
    AdmissionListSerializer, AdmissionPostSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson


class AdmissionFilter(filters.FilterSet):
    person = filters.CharFilter(field_name="person_information__person__uuid")

    class Meta:
        model = Admission
        fields = ['person_information', 'formation', 'state']


class AdmissionListCreate(generics.ListCreateAPIView):
    """
       Return a list of all the admission with optional filtering or create one.
    """
    name = 'admission-list-create'

    filter_fields = (
        'person_information',
        'formation',
        'state'
    )
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
        person = get_object_or_404(ContinuingEducationPerson, uuid=self.kwargs['uuid'])
        return Admission.objects.filter(person_information=person).select_related(
            'person_information',
            'citizenship',
            'address',
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdmissionPostSerializer
        return AdmissionListSerializer


class AdmissionDetailUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
        Return the detail of the admission, update or destroy it
    """
    name = 'admission-detail-update-destroy'
    queryset = Admission.admission_objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AdmissionPostSerializer
        return AdmissionDetailSerializer

    def get_object(self):
        admission = get_object_or_404(Admission, uuid=self.kwargs['admission_uuid'])
        return admission
