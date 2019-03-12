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

from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.prospect import ProspectFactory


class ProspectListTestCase(TestCase):
    def setUp(self):
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)

    def test_prospect_list_ordered_by_formation(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_groups = [EducationGroupFactory() for _ in range(1, 3)]

        acronyms = ['AAA', 'BBA', 'CAA']
        for index, education_group in enumerate(self.education_groups):
            EducationGroupYearFactory(
                acronym=acronyms[index],
                education_group=education_group,
                academic_year=self.academic_year
            )

        prospects = [
            ProspectFactory(
                formation=ContinuingEducationTrainingFactory(
                    education_group=education_group
                )
            ) for education_group in self.education_groups
        ]

        response = self.client.get(reverse('prospects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prospects.html')

        for index, object in enumerate(response.context['prospects'].object_list):
            self.assertEqual(response.context['prospects'].object_list[index], prospects[index])

    def test_prospect_list_no_result(self):
        response = self.client.post(reverse('prospects'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['prospects'].object_list, [])
        self.assertTemplateUsed(response, 'prospects.html')

    def test_prospect_list_logout_unauthorized(self):
        self.client.logout()
        url = reverse('prospects')
        response = self.client.get(url)
        self.assertRedirects(response, "/login/?next={}".format(url))
