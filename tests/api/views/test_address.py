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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.models.address import Address
from continuing_education.tests.factories.address import AddressFactory
from reference.tests.factories.country import CountryFactory


class GetAllAddressTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:address-list-create')

        cls.country = CountryFactory()

        AddressFactory(country=cls.country)
        AddressFactory(country=cls.country)
        AddressFactory(country=cls.country)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_address_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = Address.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)


class GetAddressTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = CountryFactory()

        cls.address = AddressFactory(country=cls.country)
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:address-detail', kwargs={'uuid': cls.address.uuid})

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_valid_address(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AddressSerializer(
            self.address,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_address_case_not_found(self):
        invalid_url = reverse('continuing_education_api_v1:address-detail', kwargs={'uuid':  uuid.uuid4()})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CreateAddressTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.country = CountryFactory()

        cls.address = AddressFactory(country=cls.country)
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:address-list-create',
            kwargs={'uuid': cls.address.uuid}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_valid_address(self):
        self.assertEqual(0, Address.objects.all().count())

        data = {
            'location': self.address.location,
            'postal_code': self.address.postal_code,
            'city': self.address.city,
            'country': self.address.country.iso_code,
        }
        response = self.client.post(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(1, Address.objects.all().count())

    def test_create_invalid_address_case_not_found(self):
        invalid_url = reverse(
            'continuing_education_api_v1:address-list-create',
            kwargs={'uuid':  uuid.uuid4()}
        )
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
