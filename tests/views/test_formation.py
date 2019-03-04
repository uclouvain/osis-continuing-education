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

from django.urls import reverse
from django.test import TestCase

from base.tests.factories.person import PersonWithPermissionsFactory
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.models.enums import education_group_types
from django.core import paginator as django_paginator


class ViewFormationTestCase(TestCase):
    def setUp(self):
        continuing_education_group_type = EducationGroupTypeFactory(
            name=education_group_types.TrainingType.AGGREGATION.name,
        )

        current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        self.previous_acad_year = AcademicYearFactory(year=current_acad_year.year - 1)

        self.formation_AAAA = EducationGroupYearFactory(
            acronym="AAAA",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.formation_BBBB = EducationGroupYearFactory(
            acronym="BBBB",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.formation_ABBB = EducationGroupYearFactory(
            acronym="ABBB",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.current_academic_formation = EducationGroupYearFactory(
            academic_year=current_acad_year,
            education_group_type=continuing_education_group_type
        )

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)
        self.entity_version = EntityVersionFactory(
            entity=self.formation_AAAA.management_entity,
        )

    def test_current_year_formation_list(self):
        response = self.client.get(reverse('formation'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['formations'].object_list[0], self.formation_AAAA)
        self.assertEqual(response.context['formations'].object_list[1], self.formation_ABBB)
        self.assertEqual(response.context['formations'].object_list[2], self.formation_BBBB)

    def test_formation_list_no_result(self):
        response = self.client.post(reverse('formation'), data={'academic_year': self.previous_acad_year})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['formations'].object_list, [])

    def test_formation_list(self):
        response = self.client.get(reverse('formation'),
                                   data={'academic_year': self.previous_acad_year, 'acronym': 'A'})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['formations'].object_list[0], self.formation_AAAA)
        self.assertEqual(response.context['formations'].object_list[1], self.formation_ABBB)


