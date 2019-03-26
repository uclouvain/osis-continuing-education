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

from base.models.person import Person
from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer, \
    ContinuingEducationPersonPostSerializer
from continuing_education.models.continuing_education_person import ContinuingEducationPerson


class ContinuingEducationPersonListCreate(generics.ListCreateAPIView):
    """
       Return a list of continuing education persons with optional filtering or create one.
    """
    name = 'person-list-create'
    queryset = ContinuingEducationPerson.objects.all().select_related(
        'person'
    )
    filter_fields = (
        'person',
    )
    search_fields = (
        'person',
    )
    ordering_fields = (
        'birth_date',
    )
    ordering = (
        'person',
    )  # Default ordering

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ContinuingEducationPersonPostSerializer
        return ContinuingEducationPersonSerializer


class ContinuingEducationPersonDetail(generics.RetrieveAPIView):
    """
        Return the detail of the continuing education person.
    """
    name = 'person-detail'
    queryset = ContinuingEducationPerson.objects.all()
    serializer_class = ContinuingEducationPersonSerializer

    def get_object(self):
        try:
            return ContinuingEducationPerson.objects.get(person__user=self.request.user)
        except ContinuingEducationPerson.DoesNotExist:
            person, _ = Person.objects.get_or_create(email=self.request.user.username)
            person.user = self.request.user
            person.save()
            return ContinuingEducationPerson.objects.create(person=person)
