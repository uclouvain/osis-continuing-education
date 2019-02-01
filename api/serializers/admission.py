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
from continuing_education.models.admission import Admission
from education_group.api.serializers.training import TrainingListSerializer
from reference.models.country import Country


class AdmissionListSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='continuing_education_api_v1:admission-detail',
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


class AdmissionDetailSerializer(serializers.HyperlinkedModelSerializer):
    person_information = ContinuingEducationPersonSerializer()

    citizenship = serializers.SlugRelatedField(
        slug_field='iso_code',
        queryset=Country.objects.all(),
    )

    main_address = AddressSerializer(source='address', read_only=True)

    # Display human readable value
    professional_status_text = serializers.CharField(source='get_professional_status_display', read_only=True)
    activity_sector_text = serializers.CharField(source='get_activity_sector_display', read_only=True)
    state_text = serializers.CharField(source='get_state_display', read_only=True)

    formation = TrainingListSerializer()

    class Meta:
        model = Admission
        fields = (
            'uuid',
            'person_information',

            # CONTACTS
            'main_address',
            'citizenship',
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
