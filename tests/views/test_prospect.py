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

from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.prospect import ProspectFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class ProspectListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationTrainingManagerFactory()

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_prospect_list_ordered_by_formation(self):
        self.academic_year = create_current_academic_year()
        self.education_groups = [EducationGroupFactory() for _ in range(1, 3)]

        acronyms = ['AAA', 'BBA', 'CAA']
        prospects = []
        for index, education_group in enumerate(self.education_groups):
            EducationGroupYearFactory(
                acronym=acronyms[index],
                education_group=education_group,
                academic_year=self.academic_year
            )
            training = ContinuingEducationTrainingFactory(education_group=education_group)
            ContinuingEducationTrainingManagerFactory(training=training, person=self.manager.person)
            prospects.append(ProspectFactory(formation=training))

        response = self.client.get(reverse('prospects'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prospects.html')

        for index, object in enumerate(response.context['prospects'].object_list):
            self.assertEqual(response.context['prospects'].object_list[index], prospects[index])
        self.assertEqual(response.context['prospects_count'], len(prospects))

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


class ProspectDetailsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.prospect = ProspectFactory()
        EducationGroupYearFactory(
            education_group=cls.prospect.formation.education_group,
            academic_year=create_current_academic_year()
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_prospect_details(self):
        response = self.client.get(reverse('prospect_details', kwargs={'prospect_id': self.prospect.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'prospect_details.html')
        context = response.context[0].dicts[3]
        self.assertEqual(
            context.get('prospect'),
            self.prospect
        )

    def test_prospect_details_unexisting_prospect(self):
        response = self.client.get(reverse('prospect_details', kwargs={'prospect_id': self.prospect.pk + 1}))
        self.assertEqual(response.status_code, 404)
