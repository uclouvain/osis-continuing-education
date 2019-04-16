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
from rest_framework import serializers

from base.api.serializers.person import PersonDetailSerializer
from base.models.person import Person
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from reference.api.serializers.country import CountrySerializer
from reference.models.country import Country


class ContinuingEducationPersonSerializer(serializers.HyperlinkedModelSerializer):
    person = PersonDetailSerializer(read_only=True)

    birth_country = CountrySerializer(read_only=True)

    class Meta:
        model = ContinuingEducationPerson
        fields = (
            'id',
            'uuid',
            'person',
            'birth_date',
            'birth_location',
            'birth_country',
        )


class ContinuingEducationPersonPostSerializer(ContinuingEducationPersonSerializer):
    person = PersonDetailSerializer()

    birth_country = serializers.SlugRelatedField(
        slug_field='iso_code',
        queryset=Country.objects.all(),
    )

    def create(self, validated_data):
        person_data = validated_data.pop('person')
        Person.objects.filter(email=person_data['email']).update(**person_data)
        person = Person.objects.get(email=person_data['email'])
        validated_data['person'] = person

        iufc_person = ContinuingEducationPerson.objects.create(**validated_data)
        return iufc_person
