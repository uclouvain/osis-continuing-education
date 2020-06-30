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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.templatetags.formation import action_disabled, DISABLED
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person_training import PersonTrainingFactory


class TestFormation(TestCase):
    @classmethod
    def setUpTestData(cls):
        academic_year = create_current_academic_year()
        academic_year_next = AcademicYearFactory(year=academic_year.year + 1)
        cls.ed = EducationGroupFactory()
        cls.education_group_year = EducationGroupYearFactory(education_group=cls.ed, academic_year=academic_year)
        cls.education_group_year_next_year = EducationGroupYearFactory(education_group=cls.ed,
                                                                       academic_year=academic_year_next)
        cls.active_formation = ContinuingEducationTrainingFactory(education_group=cls.ed, active=True)
        cls.person_training = PersonTrainingFactory(training=cls.active_formation)

        ed2 = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed2)
        cls.formation_not_managed = ContinuingEducationTrainingFactory(education_group=ed2)

    def test_action_disabled_no_trainings_managing(self):
        context = {'formation': self.active_formation,
                   'continuing_education_training_manager': True,
                   'trainings_managing': None}

        self.assertEqual(action_disabled(context, formation=self.active_formation), DISABLED)

    def test_action_disabled_no_person_training(self):
        context = {'formation': self.active_formation,
                   'continuing_education_training_manager': True,
                   'trainings_managing': [self.formation_not_managed.id]}

        self.assertEqual(action_disabled(context, formation=self.active_formation), DISABLED)

    def test_action_disabled_not_yet_continuing_education_manager(self):
        context = {'formation': '',
                   'continuing_education_training_manager': True,
                   'trainings_managing': None}

        self.assertEqual(action_disabled(context, formation=self.active_formation), DISABLED)

    def test_action_enabled_not_continuing_education_training_manager(self):
        context = {'formation': self.active_formation,
                   'continuing_education_training_manager': False,
                   'trainings_managing': None}

        self.assertEqual(action_disabled(context, formation=self.active_formation), '')

    def test_action_enabled_continuing_education_manager(self):
        context = {'continuing_education_training_manager': False}

        self.assertEqual(action_disabled(context, formation=self.active_formation), '')

    def test_action_disabled_person_training(self):
        context = {'formation': self.active_formation,
                   'continuing_education_training_manager': True,
                   'trainings_managing': [self.active_formation.id]}

        self.assertEqual(action_disabled(context, formation=self.active_formation), "")
