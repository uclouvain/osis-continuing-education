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

from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from education_group.api.serializers.training import TrainingListSerializer


class RegistrationListSerializer(serializers.HyperlinkedModelSerializer):

    url = serializers.HyperlinkedIdentityField(
        view_name='continuing_education_api_v1:registration-detail-update-destroy',
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
            'formation',
            'state',
            'state_text',
        )


class RegistrationDetailSerializer(serializers.HyperlinkedModelSerializer):
    person_information = ContinuingEducationPersonSerializer(required=False)

    main_address = AddressSerializer(source='address', required=False)
    billing_address = AddressSerializer(required=False)
    residence_address = AddressSerializer(required=False)

    # Display human readable value
    registration_type_text = serializers.CharField(source='get_registration_type_display', read_only=True)
    marital_status_text = serializers.CharField(source='get_marital_status_display', read_only=True)
    state_text = serializers.CharField(source='get_state_display', read_only=True)

    formation = TrainingListSerializer(required=False)

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'person_information',
            'formation',

            # CONTACTS
            'main_address',

            'state',
            'state_text',

            # REGISTRATION
            # BILLING
            'registration_type',
            'registration_type_text',
            'use_address_for_billing',
            'billing_address',
            'head_office_name',
            'company_number',
            'vat_number',

            # REGISTRATION
            'national_registry_number',
            'id_card_number',
            'passport_number',
            'marital_status',
            'marital_status_text',
            'spouse_name',
            'children_number',
            'previous_ucl_registration',
            'previous_noma',

            # POST
            'use_address_for_post',
            'residence_address',
            'residence_phone',

            # STUDENT SHEET
            'ucl_registration_complete',
            'noma',
            'payment_complete',
            'formation_spreading',
            'prior_experience_validation',
            'assessment_presented',
            'assessment_succeeded',
            'sessions'

        )

    def update(self, instance, validated_data):
        if 'residence_address' in validated_data:
            r_address_data = validated_data.pop('residence_address')
            r_address, created = Address.objects.update_or_create(**r_address_data)
            instance.residence_address = r_address
        if 'billing_address' in validated_data:
            b_address_data = validated_data.pop('billing_address')
            b_address, created = Address.objects.update_or_create(**b_address_data)
            instance.billing_address = b_address
        return super().update(instance, validated_data)
