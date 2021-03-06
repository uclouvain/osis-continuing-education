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
from django.test import TestCase, RequestFactory
from django.urls import reverse

from continuing_education.api.serializers.continuing_education_person import ContinuingEducationPersonSerializer, \
    ContinuingEducationPersonPostSerializer
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class ContinuingEducationPersonSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.birth_country = CountryFactory()

        cls.continuing_education_person = ContinuingEducationPersonFactory(
            birth_country=cls.birth_country
        )
        url = reverse('continuing_education_api_v1:person-list-create')
        cls.serializer = ContinuingEducationPersonSerializer(
            cls.continuing_education_person,
            context={'request': RequestFactory().get(url)}
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'uuid',
            'person',
            'birth_date',
            'birth_location',
            'birth_country',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)


class ContinuingEducationPersonPostSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.birth_country = CountryFactory()

        cls.continuing_education_person = ContinuingEducationPersonFactory(
            birth_country=cls.birth_country
        )
        url = reverse('continuing_education_api_v1:person-list-create')
        cls.serializer = ContinuingEducationPersonPostSerializer(
            cls.continuing_education_person,
            context={'request': RequestFactory().get(url)}
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'id',
            'uuid',
            'person',
            'birth_date',
            'birth_location',
            'birth_country',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_birth_country_field_is_slugified(self):
        self.assertEqual(
            self.serializer.data['birth_country'],
            self.birth_country.iso_code
        )
