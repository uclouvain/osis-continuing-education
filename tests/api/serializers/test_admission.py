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
from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from continuing_education.api.serializers.admission import AdmissionListSerializer, AdmissionDetailSerializer
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class AdmissionListSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_information = ContinuingEducationPersonFactory()
        cls.admission = AdmissionFactory(
            person_information=cls.person_information,
        )
        url = reverse('continuing_education_api_v1:admission-list-create')
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
        cls.academic_year = AcademicYearFactory(year=2018)
        new_ac = AcademicYearFactory(year=cls.academic_year.year+1)
        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=cls.person_information,
        )
        url = reverse(
            'continuing_education_api_v1:admission-detail-update-destroy',
            kwargs={'uuid': cls.admission.uuid}
        )
        cls.serializer = AdmissionDetailSerializer(cls.admission, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'uuid',
            'person_information',
            'main_address',
            'citizenship',
            'phone_mobile',
            'email',
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
            'professional_impact',
            'formation',
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
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
