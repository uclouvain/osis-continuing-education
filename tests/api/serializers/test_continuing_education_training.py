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

from base.models.enums.entity_type import FACULTY
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.api.serializers.continuing_education_training import ContinuingEducationTrainingSerializer
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ContinuingEducationTrainingSerializerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        edy = EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        EntityVersionFactory(entity=edy.management_entity, entity_type=FACULTY)
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group=cls.education_group)
        url = reverse('continuing_education_api_v1:continuing-education-training-list')
        cls.serializer = ContinuingEducationTrainingSerializer(
            cls.continuing_education_training,
            context={'request': RequestFactory().get(url)}
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            'url',
            'uuid',
            'acronym',
            'title',
            'faculty',
            'active',
            'managers',
            'training_aid'
        ]
        self.assertListEqual(list(self.serializer.data.keys()), expected_fields)
        self.assertEqual(type(self.serializer.data['managers']), list)
