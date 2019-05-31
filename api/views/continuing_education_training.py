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
from django_filters import rest_framework as filters
from rest_framework import generics

from continuing_education.api.serializers.continuing_education_training import ContinuingEducationTrainingSerializer, \
    ContinuingEducationTrainingPostSerializer
from continuing_education.models.continuing_education_training import ContinuingEducationTraining


class ContinuingEducationTrainingFilter(filters.FilterSet):
    acronym = filters.CharFilter(field_name="education_group__educationgroupyear__acronym")

    class Meta:
        model = ContinuingEducationTraining
        fields = ['education_group', 'active']


class ContinuingEducationTrainingListCreate(generics.ListCreateAPIView):
    """
       Return a list of all the trainings with optional filtering or create a training.
    """
    name = 'continuing-education-training-list-create'
    queryset = ContinuingEducationTraining.objects.all().distinct()
    filter_class = ContinuingEducationTrainingFilter
    search_fields = (
        'education_group__educationgroupyear__acronym',
    )
    ordering = (
        'education_group__educationgroupyear__acronym',
    )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContinuingEducationTrainingPostSerializer
        return ContinuingEducationTrainingSerializer


class ContinuingEducationTrainingDetailUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
        Return the detail of the training, destroy one or update one.
    """
    name = 'continuing-education-training-detail-update-delete'
    queryset = ContinuingEducationTraining.objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ContinuingEducationTrainingPostSerializer
        return ContinuingEducationTrainingSerializer
