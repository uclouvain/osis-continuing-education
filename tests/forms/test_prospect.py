##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.business.prospect import get_prospects_by_user
from continuing_education.forms.search import ProspectFilterForm
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.prospect import ProspectFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class TestProspect(TestCase):

    @classmethod
    def setUpTestData(cls):
        academic_year = create_current_academic_year()
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=education_group,
            academic_year=academic_year
        )
        training_1 = ContinuingEducationTrainingFactory(education_group=education_group)
        cls.manager = ContinuingEducationTrainingManagerFactory(training=training_1)
        cls.prospect_1 = ProspectFactory(formation=training_1, name="Delwart")
        cls.prospect_2 = ProspectFactory(formation=training_1, name="Debouche")


    def test_get_prospects_by_user(self):

        form = ProspectFilterForm(data={}, user=self.manager.person.user)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(
            form.get_propects_with_filter(),
            [self.prospect_1, self.prospect_2]
        )

    def test_get_prospects_by_user_and_free_texte(self):
        form = ProspectFilterForm(data={'free_text': 'wart'}, user=self.manager.person.user)

        self.assertTrue(form.is_valid())
        self.assertCountEqual(
            form.get_propects_with_filter(),
            [self.prospect_1, self.prospect_2]
        )
