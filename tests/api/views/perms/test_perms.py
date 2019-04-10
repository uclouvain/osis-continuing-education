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
from rest_framework.test import APIRequestFactory, APITestCase

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.views.perms.perms import HasAdmissionAccess, CanSubmitRegistration
from continuing_education.models.enums.admission_state_choices import ACCEPTED, REGISTRATION_SUBMITTED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class TestHasAdmissionAccess(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.permission = HasAdmissionAccess()
        cls.user = UserFactory()
        person_information = ContinuingEducationPersonFactory(
            person=PersonFactory(user=cls.user)
        )
        cls.admission = AdmissionFactory(person_information=person_information)

    def setUp(self):
        self.client.login(user=self.user)

    def test_hasadmissionaccess_return_true_if_owner_of_admission(self):
        request = APIRequestFactory(user=self.user)
        request.user = self.user
        self.assertTrue(
            self.permission.has_object_permission(request, None, self.admission)
        )

    def test_hasadmissionaccess_return_false_if_not_owner_of_admission(self):
        other_user = UserFactory()
        request = APIRequestFactory(user=other_user)
        request.user = other_user
        self.assertFalse(
            self.permission.has_object_permission(request, None, self.admission)
        )


class TestCanSubmitRegistration(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.permission = CanSubmitRegistration()
        cls.user = UserFactory()
        cls.request = APIRequestFactory(user=cls.user)
        cls.request.method = 'POST'
        person_information = ContinuingEducationPersonFactory(
            person=PersonFactory(user=cls.user)
        )
        cls.admission = AdmissionFactory(
            person_information=person_information
        )
        print(cls.admission.state)

    def setUp(self):
        self.client.login(user=self.user)

    def test_cansubmitregistration_return_false_if_admission_state_not_accepted(self):
        self.admission.state = REGISTRATION_SUBMITTED
        self.admission.save()
        self.assertFalse(
            self.permission.has_object_permission(self.request, None, self.admission)
        )

    def test_cansubmitregistration_return_true_if_admission_state_accepted(self):
        self.admission.state = ACCEPTED
        self.admission.save()
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, self.admission)
        )

    def test_cansubmitregistration_return_true_if_not_safe_methods(self):
        self.admission.state = REGISTRATION_SUBMITTED
        self.admission.save()
        self.request.method = 'GET'
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, self.admission)
        )
