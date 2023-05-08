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
import datetime
import uuid
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.urls import reverse
from factory.fuzzy import FuzzyText
from rest_framework import status
from rest_framework.test import APITestCase

from backoffice.settings.base import MAX_UPLOAD_SIZE
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.file import AdmissionFileSerializer, AdmissionFilePostSerializer
from continuing_education.models.file import AdmissionFile, MAX_ADMISSION_FILE_NAME_LENGTH
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class AdmissionFileListCreateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        person_information = ContinuingEducationPersonFactory()
        cls.admission = AdmissionFactory(person_information=person_information)
        cls.url = reverse('continuing_education_api_v1:file-list-create', kwargs={'uuid': cls.admission.uuid})
        for x in range(4):
            AdmissionFileFactory(
                admission=cls.admission,
                uploaded_by=person_information.person
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('continuing_education.api.serializers.file.AdmissionFileSerializer.get_content', return_value='content')
    def test_get_all_file_ensure_response_have_next_previous_results_count(self, mock_get_content):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn('previous', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)

        self.assertIn('count', response.data)
        expected_count = AdmissionFile.objects.filter(admission=self.admission).count()
        self.assertEqual(response.data['count'], expected_count)

    @patch('continuing_education.api.serializers.file.AdmissionFileSerializer.get_content', return_value='content')
    def test_create_valid_file(self, mock_get_content):
        self.assertEqual(4, AdmissionFile.objects.all().count())

        admission_file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode("test_content"),
            content_type="application/pdf"
        )
        data = {
            'name': admission_file.name,
            'size': admission_file.size,
            'uploaded_by': self.admission.person_information.person.uuid,
            'created_date': datetime.datetime.today(),
            'path': admission_file
        }
        response = self.client.post(self.url, data=data, format='multipart')

        serializer = AdmissionFilePostSerializer(
            AdmissionFile.objects.all().last(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(5, AdmissionFile.objects.all().count())

    def test_create_file_with_name_too_long(self):
        long_name = '{}.pdf'.format(FuzzyText(length=MAX_ADMISSION_FILE_NAME_LENGTH + 10).fuzz())
        admission_file = SimpleUploadedFile(
            name=long_name,
            content=str.encode("test_content"),
        )
        data = {
            'name': admission_file.name,
            'size': admission_file.size,
            'uploaded_by': self.admission.person_information.person.uuid,
            'created_date': datetime.datetime.today(),
            'path': admission_file
        }
        response = self.client.post(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_file_with_unallowed_extension(self):
        admission_file = SimpleUploadedFile(
            name='upload_test.xyz',
            content=str.encode("test_content"),
        )
        data = {
            'name': admission_file.name,
            'size': admission_file.size,
            'uploaded_by': self.admission.person_information.person.uuid,
            'created_date': datetime.datetime.today(),
            'path': admission_file
        }
        response = self.client.post(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_file_with_size_too_large(self):
        large_file_size = MAX_UPLOAD_SIZE + 1
        admission_file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode("test_content"),
            content_type="application/pdf"
        )
        data = {
            'name': admission_file.name,
            'size': large_file_size,
            'uploaded_by': self.admission.person_information.person.uuid,
            'created_date': datetime.datetime.today(),
            'path': admission_file
        }
        response = self.client.post(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    def test_create_invalid_file(self):
        invalid_url = reverse(
            'continuing_education_api_v1:file-list-create',
            kwargs={'uuid':  uuid.uuid4()}
        )
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdmissionFileRetrieveDestroy(APITestCase):
    @classmethod
    def setUpTestData(cls):
        person_information = ContinuingEducationPersonFactory()
        cls.admission_file = AdmissionFileFactory(
            uploaded_by=person_information.person
        )
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:file-detail-delete',
            kwargs={'file_uuid': cls.admission_file.uuid, 'uuid': cls.admission_file.admission.uuid}
        )

        cls.invalid_url = reverse(
            'continuing_education_api_v1:file-detail-delete',
            kwargs={'uuid':  uuid.uuid4(), 'file_uuid': uuid.uuid4()}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'put']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @patch('continuing_education.api.serializers.file.AdmissionFileSerializer.get_content', return_value='content')
    def test_get_valid_file(self, mock_get_content):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionFileSerializer(
            self.admission_file,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_file_case_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_valid_file(self):
        self.assertEqual(1, AdmissionFile.objects.all().count())
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, AdmissionFile.objects.all().count())

    def test_delete_invalid_file_case_not_found(self):
        response = self.client.delete(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
