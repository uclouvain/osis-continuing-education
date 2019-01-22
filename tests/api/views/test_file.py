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
from unittest.mock import patch

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.file import FileSerializer
from continuing_education.models.file import File
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import FileFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class GetAllFileTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        person_information = ContinuingEducationPersonFactory()
        cls.admission = AdmissionFactory(person_information=person_information)
        cls.url = reverse('continuing_education_api_v1:file-list', kwargs={'uuid': cls.admission.uuid})
        FileFactory(
            admission=cls.admission,
            uploaded_by=person_information.person
        )
        FileFactory(
            admission=cls.admission,
            uploaded_by=person_information.person
        )
        FileFactory(
            admission=cls.admission,
            uploaded_by=person_information.person
        )
        FileFactory(
            admission=cls.admission,
            uploaded_by=person_information.person
        )

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

    @patch('continuing_education.api.serializers.file.FileSerializer.get_content', return_value='content')
    def test_get_all_file_ensure_response_have_next_previous_results_count(self, mock_get_content):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = File.objects.filter(admission=self.admission).count()
        self.assertEqual(response.data['count'], expected_count)


class GetFileTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        person_information = ContinuingEducationPersonFactory()
        cls.file = FileFactory(
            uploaded_by=person_information.person
        )
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:file-detail',
            kwargs={'file_uuid': cls.file.uuid, 'uuid': cls.file.admission.uuid}
        )

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

    @patch('continuing_education.api.serializers.file.FileSerializer.get_content', return_value='content')
    def test_get_valid_file(self, mock_get_content):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = FileSerializer(
            self.file,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_file_case_not_found(self):
        invalid_url = reverse(
            'continuing_education_api_v1:file-detail',
            kwargs={'uuid':  uuid.uuid4(), 'file_uuid': uuid.uuid4()}
        )
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DeleteFileTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        person_information = ContinuingEducationPersonFactory()
        cls.file = FileFactory(
            uploaded_by=person_information.person
        )
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:file-delete',
            kwargs={'file_uuid': cls.file.uuid, 'uuid': cls.file.admission.uuid}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_delete_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'get', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_valid_file(self):
        self.assertEqual(1, File.objects.all().count())
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, File.objects.all().count())

    def test_delete_invalid_file_case_not_found(self):
        invalid_url = reverse(
            'continuing_education_api_v1:file-delete',
            kwargs={'uuid':  uuid.uuid4(), 'file_uuid': uuid.uuid4()}
        )
        response = self.client.delete(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
