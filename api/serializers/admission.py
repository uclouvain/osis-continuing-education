##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.person import Person
from continuing_education.api.serializers.address import AddressSerializer, AddressPostSerializer
from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer, \
    ContinuingEducationPersonPostSerializer
from continuing_education.api.serializers.continuing_education_training import ContinuingEducationTrainingSerializer
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from reference.api.serializers.country import CountrySerializer
from reference.models.country import Country


class AdmissionListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='continuing_education_api_v1:admission-detail-update',
        lookup_field='uuid'
    )

    person_information = ContinuingEducationPersonSerializer()

    # Display human readable value
    state_text = serializers.CharField(source='get_state_display', read_only=True)

    formation = ContinuingEducationTrainingSerializer()

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'url',
            'person_information',
            'email',
            'formation',
            'state',
            'state_text',
        )


class AdmissionDetailSerializer(AdmissionListSerializer):
    citizenship = CountrySerializer()

    address = AddressSerializer()

    # Display human readable value
    professional_status_text = serializers.CharField(source='get_professional_status_display', read_only=True)
    activity_sector_text = serializers.CharField(source='get_activity_sector_display', read_only=True)

    class Meta:
        model = Admission
        fields = AdmissionListSerializer.Meta.fields + (
            # CONTACTS
            'address',
            'citizenship',
            'phone_mobile',

            # EDUCATION
            'high_school_diploma',
            'high_school_graduation_year',
            'last_degree_level',
            'last_degree_field',
            'last_degree_institution',
            'last_degree_graduation_year',
            'other_educational_background',

            # PROFESSIONAL BACKGROUND
            'professional_status',
            'professional_status_text',
            'current_occupation',
            'current_employer',
            'activity_sector',
            'activity_sector_text',
            'past_professional_activities',

            # MOTIVATION
            'motivation',
            'professional_impact',

            # AWARENESS
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_other',
        )


class AdmissionPostSerializer(AdmissionDetailSerializer):
    citizenship = serializers.SlugRelatedField(
        slug_field='iso_code',
        queryset=Country.objects.all(),
        required=False,
        allow_null=True
    )
    address = AddressPostSerializer(required=False, allow_null=True)
    person_information = ContinuingEducationPersonPostSerializer(required=True)
    formation = serializers.SlugRelatedField(
        queryset=ContinuingEducationTraining.objects.all(),
        slug_field='uuid',
        required=True
    )

    def update(self, instance, validated_data):
        self.update_field('address', validated_data, instance.address)
        if 'person_information' in validated_data:
            validated_data.pop('person_information')
        return super(AdmissionDetailSerializer, self).update(instance, validated_data)

    def update_field(self, field, validated_data, instance):
        if field in validated_data:
            field_serializer = self.fields[field]
            field_data = validated_data.pop(field)
            field_serializer.update(instance, field_data)

    def create(self, validated_data):
        if 'person_information' in validated_data:
            iufc_person_data = validated_data.pop('person_information')
            person_data = iufc_person_data.pop('person')

            Person.objects.filter(email=person_data['email']).update(**person_data)
            person = Person.objects.get(email=person_data['email'])
            ContinuingEducationPerson.objects.filter(person=person).update(**iufc_person_data)
            iufc_person = ContinuingEducationPerson.objects.get(person=person)
            validated_data['person_information'] = iufc_person

        formation_data = validated_data.pop('formation', None)
        validated_data['formation'] = formation_data
        if 'address' in validated_data:
            address_data = validated_data.pop('address')
            address = Address.objects.create(**address_data)
            validated_data['address'] = address
        admission = Admission(**validated_data)
        admission.residence_address = admission.address
        admission.billing_address = admission.address
        admission.save()
        return admission
