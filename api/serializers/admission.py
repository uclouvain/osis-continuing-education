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

from base.models.education_group_year import EducationGroupYear
from base.models.person import Person
from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer, \
    ContinuingEducationPersonPostSerializer
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from education_group.api.serializers.training import TrainingListSerializer
from reference.api.serializers.country import CountrySerializer


class AdmissionListSerializer(serializers.HyperlinkedModelSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        context = kwargs.get('context', None)
        if context:
            request = kwargs['context']['request']

            if request.method == 'POST':
                self.fields['person_information'] = ContinuingEducationPersonPostSerializer()
            else:
                self.fields['person_information'] = ContinuingEducationPersonSerializer()

    url = serializers.HyperlinkedIdentityField(
        view_name='continuing_education_api_v1:admission-detail-update-destroy',
        lookup_field='uuid'
    )
    person_information = ContinuingEducationPersonSerializer()

    # Display human readable value
    state_text = serializers.CharField(source='get_state_display', read_only=True)

    formation = TrainingListSerializer()

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

    def create(self, validated_data):
        iufc_person_data = validated_data.pop('person_information')
        person_data = iufc_person_data.pop('person')
        formation_data = validated_data.pop('formation')

        person, created = Person.objects.get_or_create(**person_data)

        iufc_person, created = ContinuingEducationPerson.objects.get_or_create(
            person=person,
            **iufc_person_data
        )
        validated_data['person_information'] = iufc_person

        formation = EducationGroupYear.objects.get(**formation_data)
        validated_data['formation'] = formation

        admission = Admission.objects.create(**validated_data)
        return admission


class AdmissionDetailSerializer(serializers.HyperlinkedModelSerializer):
    person_information = ContinuingEducationPersonSerializer(required=False)

    citizenship = CountrySerializer(required=False)
    citizenship_text = serializers.CharField(source='citizenship.iso_code', read_only=True)

    main_address = AddressSerializer(source='address', required=False)

    # Display human readable value
    professional_status_text = serializers.CharField(source='get_professional_status_display', read_only=True)
    activity_sector_text = serializers.CharField(source='get_activity_sector_display', read_only=True)
    state_text = serializers.CharField(source='get_state_display', read_only=True)

    formation = TrainingListSerializer(required=False)
    formation_text = serializers.CharField(source='formation.acronym', read_only=True)

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'person_information',

            # CONTACTS
            'main_address',
            'citizenship',
            'citizenship_text',
            'phone_mobile',
            'email',

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
            'formation',
            'formation_text',

            # AWARENESS
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_other',

            'state',
            'state_text',

            # # REGISTRATION
            # # BILLING
            # 'registration_type',
            # 'registration_type_text',
            # 'use_address_for_billing',
            # 'billing_address',
            # 'head_office_name',
            # 'company_number',
            # 'vat_number',
            #
            # # REGISTRATION
            # 'national_registry_number',
            # 'id_card_number',
            # 'passport_number',
            # 'marital_status',
            # 'marital_status_text',
            # 'spouse_name',
            # 'children_number',
            # 'previous_ucl_registration',
            # 'previous_noma',
            #
            # # POST
            # 'use_address_for_post',
            # 'residence_address',
            # 'residence_phone',
            #
            # # STUDENT SHEET
            # 'ucl_registration_complete',
            # 'noma',
            # 'payment_complete',
            # 'formation_spreading',
            # 'prior_experience_validation',
            # 'assessment_presented',
            # 'assessment_succeeded',
            # 'sessions'

        )

    def update(self, instance, validated_data):
        fields = instance._meta.fields
        exclude = []
        for field in fields:
            field = field.name.split('.')[-1]
            if field in exclude:
                continue
            if field == 'address' and 'address' in validated_data:
                address_data = validated_data.pop('address')
                address, created = Address.objects.update_or_create(**address_data)
                instance.address = address
            else:
                exec("instance.%s = validated_data.get(field, instance.%s)" % (field, field))
        instance.save()
        return instance
