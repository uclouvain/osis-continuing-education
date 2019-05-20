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

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class ContinuingEducationPersonListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:person-list')

        cls.birth_country = CountryFactory()
        cls.country = CountryFactory(iso_code='FR')
        cls.person = PersonFactory()
        for x in range(3):
            ContinuingEducationPersonFactory(birth_country=cls.birth_country)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch', 'post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_person_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = ContinuingEducationPerson.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)


class ContinuingEducationPersonDetailTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.birth_country = CountryFactory()
        fr = CountryFactory(iso_code='FR')

        cls.user = UserFactory()
        p = PersonFactory(user=cls.user)
        cls.person = ContinuingEducationPersonFactory(
            person=p,
            birth_country=cls.birth_country
        )
        cls.url = reverse('continuing_education_api_v1:person-detail')

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'put', 'delete']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_valid_person(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ContinuingEducationPersonSerializer(
            self.person,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
