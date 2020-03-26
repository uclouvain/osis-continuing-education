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

from base.tests.factories.group import GroupFactory
from continuing_education.business import perms
from continuing_education.models.enums.groups import TRAINING_MANAGERS_GROUP
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory


class PermsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group_training_manager = GroupFactory(name=TRAINING_MANAGERS_GROUP)
        cls.training_manager = PersonFactory()
        cls.training_manager.user.groups.add(group_training_manager)

    def test_is_continuing_education_training_manager(self):
        self.assertTrue(perms.is_continuing_education_training_manager(self.training_manager.user))
