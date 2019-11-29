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

from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.models.continuing_education_training import ContinuingEducationTraining


class PersonTrainingListField(serializers.RelatedField):

    def to_representation(self, value):
        return {
            "uuid": value.uuid,
            "first_name": value.first_name,
            "last_name": value.last_name,
            "email": value.email
        }


class ContinuingEducationTrainingSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='continuing_education_api_v1:continuing-education-training-detail',
        lookup_field='uuid'
    )
    faculty = serializers.SerializerMethodField()
    postal_address = AddressSerializer(allow_null=True)

    managers = PersonTrainingListField(many=True, read_only=True)

    class Meta:
        model = ContinuingEducationTraining
        fields = (
            'url',
            'uuid',
            'acronym',
            'title',
            'faculty',
            'active',
            'managers',
            'training_aid',
            'postal_address',
            'additional_information_label',
            'registration_required'
        )

    def get_faculty(self, obj):
        ac = obj.academic_year
        faculty_version = obj.management_entity.entityversion_set.first().find_faculty_version(ac)
        return faculty_version.acronym if faculty_version else None
