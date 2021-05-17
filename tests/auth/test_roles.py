##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from continuing_education.auth.roles.continuing_education_manager import is_continuing_education_manager
from continuing_education.auth.roles.continuing_education_student_worker import is_continuing_education_student_worker
from continuing_education.auth.roles.continuing_education_training_manager import \
    is_continuing_education_training_manager
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_student_worker import \
    ContinuingEducationStudentWorkerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class TestRoles(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.training_manager = ContinuingEducationTrainingManagerFactory()
        cls.manager = ContinuingEducationManagerFactory()
        cls.student_worker = ContinuingEducationStudentWorkerFactory()

    def test_is_continuing_education_training_manager(self):
        self.assertTrue(is_continuing_education_training_manager(self.training_manager.person.user))
        self.assertFalse(is_continuing_education_training_manager(self.manager.person.user))
        self.assertFalse(is_continuing_education_training_manager(self.student_worker.person.user))

    def test_is_continuing_education_student_worker(self):
        self.assertFalse(is_continuing_education_student_worker(self.training_manager.person.user))
        self.assertFalse(is_continuing_education_student_worker(self.manager.person.user))
        self.assertTrue(is_continuing_education_student_worker(self.student_worker.person.user))

    def test_is_continuing_education_manager(self):
        self.assertFalse(is_continuing_education_manager(self.training_manager.person.user))
        self.assertTrue(is_continuing_education_manager(self.manager.person.user))
        self.assertFalse(is_continuing_education_manager(self.student_worker.person.user))
