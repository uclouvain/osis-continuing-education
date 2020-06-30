from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.api.serializers.registration import RegistrationDetailSerializer, \
    RegistrationListSerializer, \
    RegistrationPostSerializer
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class RegistrationListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed,
            academic_year=create_current_academic_year()
        )
        cls.person_information = ContinuingEducationPersonFactory()
        cls.admission = AdmissionFactory(
            person_information=cls.person_information,
            formation=ContinuingEducationTrainingFactory(education_group=ed)
        )
        url = reverse('continuing_education_api_v1:registration-list', kwargs={'uuid': cls.person_information.uuid})
        cls.serializer = RegistrationListSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'formation',
            'state',
            'state_text',
            'email',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class RegistrationDetailSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ed = EducationGroupFactory()
        cls.person_information = ContinuingEducationPersonFactory()
        cls.academic_year = create_current_academic_year()
        EducationGroupYearFactory(education_group=ed, academic_year=cls.academic_year)
        AcademicYearFactory(year=cls.academic_year.year + 1)
        cls.admission = AdmissionFactory(
            person_information=cls.person_information,
            formation=ContinuingEducationTrainingFactory(education_group=ed)
        )
        url = reverse(
            'continuing_education_api_v1:registration-detail-update',
            kwargs={'uuid': cls.admission.uuid}
        )
        cls.serializer = RegistrationDetailSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'formation',
            'state',
            'state_text',
            'email',
            'address',
            'citizenship',
            'phone_mobile',
            'registration_type',
            'registration_type_text',
            'use_address_for_billing',
            'billing_address',
            'head_office_name',
            'company_number',
            'vat_number',
            'national_registry_number',
            'id_card_number',
            'passport_number',
            'marital_status',
            'marital_status_text',
            'spouse_name',
            'children_number',
            'previous_ucl_registration',
            'previous_noma',
            'professional_status',
            'use_address_for_post',
            'residence_address',
            'residence_phone',
            'ucl_registration_complete',
            'noma',
            'payment_complete',
            'formation_spreading',
            'prior_experience_validation',
            'assessment_presented',
            'assessment_succeeded',
            'sessions',
            'reduced_rates',
            'spreading_payments',
            'condition_of_acceptance',
            'high_school_graduation_year',
            'last_degree_graduation_year',
            'academic_yr',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class RegistrationPostSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_information = ContinuingEducationPersonFactory()
        ed = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed,
            academic_year=create_current_academic_year()
        )
        cls.formation = ContinuingEducationTrainingFactory(education_group=ed)
        cls.registration = AdmissionFactory(
            person_information=cls.person_information,
            formation=cls.formation
        )
        url = reverse(
            'continuing_education_api_v1:registration-detail-update',
            kwargs={'uuid': cls.registration.uuid}
        )
        cls.serializer = RegistrationPostSerializer(cls.registration, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'formation',
            'state',
            'state_text',
            'email',
            'address',
            'citizenship',
            'phone_mobile',
            'registration_type',
            'registration_type_text',
            'use_address_for_billing',
            'billing_address',
            'head_office_name',
            'company_number',
            'vat_number',
            'national_registry_number',
            'id_card_number',
            'passport_number',
            'marital_status',
            'marital_status_text',
            'spouse_name',
            'children_number',
            'previous_ucl_registration',
            'previous_noma',
            'professional_status',
            'use_address_for_post',
            'residence_address',
            'residence_phone',
            'ucl_registration_complete',
            'noma',
            'payment_complete',
            'formation_spreading',
            'prior_experience_validation',
            'assessment_presented',
            'assessment_succeeded',
            'sessions',
            'reduced_rates',
            'spreading_payments',
            'condition_of_acceptance',
            'high_school_graduation_year',
            'last_degree_graduation_year',
            'academic_yr',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_formation_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['formation'],
            self.formation.uuid
        )
