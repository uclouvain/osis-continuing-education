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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.formation import ContinuingEducationTrainingForm
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class TestContinuingEducationTrainingFormForm(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )

    def test_valid_form_for_continuing_education_managers(self):
        self.manager = PersonWithPermissionsFactory(groups='continuing_education_managers')
        self.client.force_login(self.manager.user)
        data = self.formation.__dict__
        data['formation'] = self.formation.pk
        form = ContinuingEducationTrainingForm(data=data, user=self.manager.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_disabled_fields_for_training_managers(self):
        self.training_manager = PersonWithPermissionsFactory(groups='continuing_education_training_managers')
        self.client.force_login(self.training_manager.user)
        form = ContinuingEducationTrainingForm(data=None, user=self.training_manager.user)
        self.assertTrue(form['training_aid'].field.disabled)
        self.assertTrue(form['active'].field.disabled)
