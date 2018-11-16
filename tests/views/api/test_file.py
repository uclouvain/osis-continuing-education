##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from continuing_education.models.file import File
from continuing_education.tests.factories.admission import AdmissionFactory

FILES_COUNT = 5
FILE_CONTENT = "test-content"

class ViewFileAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            'demo',
            'demo@demo.org',
            'passtest'
        )
        self.client.force_login(self.user)
        self.file_api_url = reverse('continuing_education_api_v1:file_api')
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.admission = AdmissionFactory()
        add_files_to_db(self.admission)
        self.file = File.objects.all().first()

    def test_unauthorized_api_access(self):
        response = self.client.get(
            path=self.file_api_url,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upload_file(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )
        file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf"
        )
        response = self.client.put(
            path=self.file_api_url,
            data={
                'file': file,
                'admission_id': self.admission.uuid
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(),FILES_COUNT+1)

    def test_get_file(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )
        response = self.client.get(
            path=self.file_api_url,
            data={'file_path': self.file.path.name}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content.decode(), FILE_CONTENT+"0")

    def test_get_files_list(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )
        response = self.client.get(
            path=self.file_api_url,
            data={'admission_id': self.admission.uuid}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json.loads(response.content.decode("utf-8"))), FILES_COUNT)

    def test_get_without_params(self):
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token.key
        )
        response = self.client.get(
            path=self.file_api_url
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


def add_files_to_db(admission):
    for i in range(0, FILES_COUNT):
        existing_file = SimpleUploadedFile(
            name=str(i)+'.pdf',
            content=str.encode(FILE_CONTENT+str(i)),
            content_type="application/pdf"
        )
        file = File(
            admission=admission,
            name=existing_file.name,
            path=existing_file
        )
        file.save()
