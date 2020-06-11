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

from base.models.education_group import EducationGroup
from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from education_group.api.serializers.training import TrainingListSerializer


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
        view_name='continuing_education_api_v1:continuing-education-training-detail-update-delete',
        lookup_field='uuid'
    )
    education_group = serializers.SerializerMethodField()
    postal_address = AddressSerializer(allow_null=True)

    managers = PersonTrainingListField(many=True, read_only=True)

    class Meta:
        model = ContinuingEducationTraining
        fields = (
            'url',
            'uuid',
            'education_group',
            'active',
            'managers',
            'training_aid',
            'postal_address',
            'additional_information_label',
            'registration_required'
        )

    def get_education_group(self, obj):
        # return last education_group_year
        education_group = obj.get_most_recent_education_group_year()
        standard_version = education_group.educationgroupversion_set.filter(
            version_name='',
            is_transition=False
        ).select_related(
            'offer',
            'offer__academic_year',
            'offer__administration_entity',
            'offer__management_entity'
        ).first()
        return TrainingListSerializer(
            standard_version,
            context={'request': self.context['request']}
        ).data


class ContinuingEducationTrainingPostSerializer(ContinuingEducationTrainingSerializer):
    education_group = serializers.SlugRelatedField(
        queryset=EducationGroup.objects.all(),
        slug_field='uuid',
        required=True
    )
