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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.prospect import ProspectSerializer
from continuing_education.models.prospect import Prospect
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.prospect import ProspectFactory


class ProspectListCreateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:prospect-list-create')
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.prospect = ProspectFactory(formation=formation)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_prospect_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = Prospect.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)

    def test_create_valid_prospect(self):
        self.assertEqual(1, Prospect.objects.all().count())
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=education_group,
            academic_year=self.academic_year
        )
        data = {
            'last_name': self.prospect.last_name,
            'first_name': self.prospect.first_name,
            'postal_code': self.prospect.postal_code,
            'city': self.prospect.city,
            'email': self.prospect.email,
            'phone_number': self.prospect.phone_number,
            'formation': ContinuingEducationTrainingFactory(
                education_group=education_group
            ).uuid
        }
        response = self.client.post(self.url, data=data, format='json')
        serializer = ProspectSerializer(
            Prospect.objects.all().last(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(2, Prospect.objects.all().count())


class ProspectDetailUpdateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.prospect = ProspectFactory(formation=formation)
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:prospect-detail-update',
            kwargs={'uuid': cls.prospect.uuid}
        )
        cls.invalid_url = reverse(
            'continuing_education_api_v1:prospect-detail-update',
            kwargs={'uuid': uuid.uuid4()}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_update_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_valid_prospect(self):
        self.assertEqual(1, Prospect.objects.all().count())
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=education_group,
            academic_year=self.academic_year
        )
        data = {
            'city': 'Dinant',
            'name': 'Pompidou',
            'email': 'fake@d.be',
            'formation': ContinuingEducationTrainingFactory(
                education_group=education_group,
            ).uuid
        }
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProspectSerializer(
            Prospect.objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Prospect.objects.all().count())

    def test_update_invalid_prospect(self):
        response = self.client.put(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_valid_prospect(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ProspectSerializer(
            self.prospect,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_prospect_case_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
