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
from unittest.mock import patch

from django.test import TestCase, RequestFactory
from django.urls import reverse

from continuing_education.api.serializers.file import AdmissionFileSerializer, AdmissionFilePostSerializer
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class AdmissionFileSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        person_information = ContinuingEducationPersonFactory()
        cls.admission = AdmissionFactory(
            person_information=person_information
        )
        cls.admission_file = AdmissionFileFactory(
            uploaded_by=person_information.person
        )
        url = reverse('continuing_education_api_v1:file-list-create', kwargs={'uuid': cls.admission.uuid})
        cls.serializer = AdmissionFileSerializer(cls.admission_file, context={'request': RequestFactory().get(url)})

    @patch('continuing_education.api.serializers.file.AdmissionFileSerializer.get_content', return_value='content')
    def test_contains_expected_fields(self, mock_get_content):
        expected_fields = [
            'url',
            'uuid',
            'name',
            'path',
            'size',
            'created_date',
            'uploaded_by',
            'content',
            'file_category',
            'file_category_text'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class AdmissionFilePostSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        person_information = ContinuingEducationPersonFactory()
        cls.uploaded_by = person_information.person
        cls.admission = AdmissionFactory(
            person_information=person_information
        )
        cls.admission_file = AdmissionFileFactory(
            uploaded_by=cls.uploaded_by
        )

        url = reverse('continuing_education_api_v1:file-list-create', kwargs={'uuid': cls.admission.uuid})
        cls.serializer = AdmissionFilePostSerializer(cls.admission_file, context={'request': RequestFactory().get(url)})

    def setUp(self):
        self.patcher = patch(
            "continuing_education.api.serializers.file.AdmissionFileSerializer.get_content",
            return_value="Test"
        )
        self.mocked_get_content = self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'name',
            'path',
            'size',
            'created_date',
            'uploaded_by',
            'content',
            'file_category',
            'file_category_text'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_uploaded_by_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['uploaded_by'],
            self.uploaded_by.uuid
        )
