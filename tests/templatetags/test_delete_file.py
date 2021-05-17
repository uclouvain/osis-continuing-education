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

from continuing_education.templatetags.delete_file import check_permission_to_delete
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory


class TestDeleteFile(TestCase):
    @classmethod
    def setUpTestData(cls):
        participant = PersonFactory()
        person_information = ContinuingEducationPersonFactory(person=participant)
        cls.admission = AdmissionFactory(
            person_information=person_information
        )
        cls.participant_file = AdmissionFileFactory(
            uploaded_by=participant
        )
        cls.manager = ContinuingEducationManagerFactory()
        cls.manager_file = AdmissionFileFactory(
            uploaded_by=cls.manager.person
        )
        other_manager = ContinuingEducationManagerFactory()
        cls.other_manager_file = AdmissionFileFactory(
            uploaded_by=other_manager.person
        )
        cls.context = {'user': cls.manager.person.user,
                       'admission': cls.admission}

    def test_different_person(self):
        self.client.force_login(user=self.manager.person.user)
        self.assertFalse(check_permission_to_delete(self.context, self.other_manager_file))

    def test_same_person(self):
        self.client.force_login(user=self.manager.person.user)
        self.assertTrue(check_permission_to_delete(self.context, self.manager_file))

    def test_delete_participant_file(self):
        self.client.force_login(user=self.manager.person.user)
        self.assertTrue(check_permission_to_delete(self.context, self.participant_file))
