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

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.tests.factories.prospect import ProspectFactory


class ProspectListTestCase(TestCase):
    def setUp(self):
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)

    def test_prospect_list_ordered_by_formation(self):
        current_acad_year = create_current_academic_year()
        formation_1 = EducationGroupYearFactory(
            acronym="AAAA",
            academic_year=current_acad_year
        )
        formation_2 = EducationGroupYearFactory(
            acronym="BBA",
            academic_year=current_acad_year
        )
        formation_3 = EducationGroupYearFactory(
            acronym="CAA",
            academic_year=current_acad_year
        )
        prospect_1 = ProspectFactory(formation=formation_1)
        prospect_2 = ProspectFactory(formation=formation_2)
        prospect_3 = ProspectFactory(formation=formation_3)

        response = self.client.get(reverse('prospects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prospects.html')

        self.assertEqual(response.context['prospects'].object_list[0], prospect_1)
        self.assertEqual(response.context['prospects'].object_list[1], prospect_2)
        self.assertEqual(response.context['prospects'].object_list[2], prospect_3)

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
