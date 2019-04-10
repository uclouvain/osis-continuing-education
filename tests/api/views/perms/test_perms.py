##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.views.perms.perms import HasAdmissionAccess
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class TestHasAdmissionAccess(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.permission = HasAdmissionAccess()
        cls.user = UserFactory()
        cls.request = APIRequestFactory(user=cls.user)

        person_information = ContinuingEducationPersonFactory(
            person=PersonFactory(user=cls.user)
        )
        cls.admission = AdmissionFactory(person_information=person_information)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_hasadmissionaccess_return_true_if_owner_of_admission(self):
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, self.admission)
        )

    def test_hasadmissionaccess_return_false_if_not_owner_of_admission(self):
        self.request.user = UserFactory()
        self.assertFalse(
            self.permission.has_object_permission(self.request, None, self.admission)
        )