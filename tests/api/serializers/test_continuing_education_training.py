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
from collections import OrderedDict
from uuid import UUID

from django.test import TestCase, RequestFactory
from django.urls import reverse

from base.tests.factories.education_group_year import TrainingFactory
from continuing_education.api.serializers.continuing_education_training import ContinuingEducationTrainingSerializer, \
    ContinuingEducationTrainingPostSerializer
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ContinuingEducationTrainingSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        training = TrainingFactory()
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group_year=training)
        url = reverse('continuing_education_api_v1:continuing-education-training-list-create')
        cls.serializer = ContinuingEducationTrainingSerializer(cls.continuing_education_training, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'education_group_year',
            'active',
            'managers',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
        self.assertEqual(type(self.serializer.data['education_group_year']), OrderedDict)


class ContinuingEducationTrainingPostSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        training = TrainingFactory()
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group_year=training)
        url = reverse('continuing_education_api_v1:continuing-education-training-list-create')
        cls.serializer = ContinuingEducationTrainingPostSerializer(cls.continuing_education_training, context={'request': RequestFactory().get(url)})

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'education_group_year',
            'active',
            'managers',
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)

    def test_ensure_education_group_year_is_slugified(self):
        self.assertEqual(
            self.serializer.data['education_group_year'],
            self.continuing_education_training.education_group_year.uuid
        )
