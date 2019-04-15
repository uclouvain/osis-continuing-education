##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.core.exceptions import ValidationError
from django.test import TestCase

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.tests.factories.person_training import PersonTrainingFactory


class TestContinuingEducationTraining(TestCase):
    def setUp(self):
        self.education_group = EducationGroupFactory()

    def test_validation_error_raised_for_training_without_education_group_year(self):
        training = ContinuingEducationTraining(education_group=self.education_group)
        with self.assertRaises(ValidationError):
            training.clean()

    def test_formation_administrators(self):
        academic_year = AcademicYearFactory(year=2018)
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=academic_year,
        )
        a_training = ContinuingEducationTraining(education_group=self.education_group)
        a_training.save()
        person_1 = PersonFactory(first_name="Louis", last_name="Lesquoy")
        person_2 = PersonFactory(first_name="Arnaud", last_name="Jadoulle")

        PersonTrainingFactory(person=person_1, training=a_training)
        PersonTrainingFactory(person=person_2, training=a_training)

        self.assertEqual(a_training.formation_administrators, "{}, {} - {}, {}".format(person_2.last_name.upper(),
                                                                                       person_2.first_name,
                                                                                       person_1.last_name.upper(),
                                                                                       person_1.first_name))
