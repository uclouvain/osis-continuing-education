from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.api.serializers.admission import AdmissionListSerializer, AdmissionDetailSerializer, \
    AdmissionPostSerializer
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class AdmissionListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_information = ContinuingEducationPersonFactory()
        ed = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed,
            academic_year=create_current_academic_year()
        )

        cls.admission = AdmissionFactory(
            person_information=cls.person_information,
            formation=ContinuingEducationTrainingFactory(education_group=ed)
        )
        url = reverse('continuing_education_api_v1:admission-list', kwargs={'uuid': cls.person_information.uuid})
        cls.serializer = AdmissionListSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'email',
            'formation',
            'state',
            'state_text',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class AdmissionDetailSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_information = ContinuingEducationPersonFactory()
        cls.citizenship = CountryFactory()
        cls.academic_year = create_current_academic_year()
        AcademicYearFactory(year=cls.academic_year.year + 1)
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed, academic_year=cls.academic_year)
        cls.formation = ContinuingEducationTrainingFactory(education_group=ed)
        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=cls.person_information,
            formation=cls.formation
        )
        url = reverse(
            'continuing_education_api_v1:admission-detail-update',
            kwargs={'uuid': cls.admission.uuid}
        )
        cls.serializer = AdmissionDetailSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'email',
            'formation',
            'state',
            'state_text',
            'address',
            'citizenship',
            'phone_mobile',
            'residence_phone',
            'high_school_diploma',
            'high_school_graduation_year',
            'last_degree_level',
            'last_degree_field',
            'last_degree_institution',
            'last_degree_graduation_year',
            'other_educational_background',
            'professional_status',
            'professional_status_text',
            'current_occupation',
            'current_employer',
            'activity_sector',
            'activity_sector_text',
            'past_professional_activities',
            'motivation',
            'professional_personal_interests',
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_word_of_mouth',
            'awareness_friends',
            'awareness_former_students',
            'awareness_moocs',
            'awareness_other',
            'state_reason',
            'condition_of_acceptance',
            'additional_information'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class AdmissionPostSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_information = ContinuingEducationPersonFactory()
        cls.citizenship = CountryFactory()
        ed = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed,
            academic_year=create_current_academic_year()
        )
        cls.formation = ContinuingEducationTrainingFactory(education_group=ed)
        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=cls.person_information,
            formation=cls.formation
        )
        url = reverse(
            'continuing_education_api_v1:admission-detail-update',
            kwargs={'uuid': cls.admission.uuid}
        )
        cls.serializer = AdmissionPostSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'url',
            'person_information',
            'email',
            'formation',
            'state',
            'state_text',
            'address',
            'citizenship',
            'phone_mobile',
            'residence_phone',
            'high_school_diploma',
            'high_school_graduation_year',
            'last_degree_level',
            'last_degree_field',
            'last_degree_institution',
            'last_degree_graduation_year',
            'other_educational_background',
            'professional_status',
            'professional_status_text',
            'current_occupation',
            'current_employer',
            'activity_sector',
            'activity_sector_text',
            'past_professional_activities',
            'motivation',
            'professional_personal_interests',
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_word_of_mouth',
            'awareness_friends',
            'awareness_former_students',
            'awareness_moocs',
            'awareness_other',
            'state_reason',
            'condition_of_acceptance',
            'additional_information'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_formation_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['formation'],
            self.formation.uuid
        )
