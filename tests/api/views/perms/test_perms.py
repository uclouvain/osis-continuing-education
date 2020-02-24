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

from rest_framework.test import APIRequestFactory, APITestCase

from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.views.perms.perms import HasAdmissionAccess, CanSubmit, CanSendFiles, \
    CanSubmitAdmission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, REGISTRATION_SUBMITTED, DRAFT, \
    REJECTED, \
    WAITING, SUBMITTED, VALIDATED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
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
        cls.permission = CanSubmit()
        cls.user = UserFactory()
        cls.request = APIRequestFactory(user=cls.user)
        cls.request.method = 'POST'
        cls.admission = AdmissionFactory()

    def setUp(self):
        self.client.login(user=self.user)

    def test_cansubmitregistration_return_false_if_admission_state_not_accepted(self):
        admission = AdmissionFactory(state=REGISTRATION_SUBMITTED)
        self.assertFalse(
            self.permission.has_object_permission(self.request, None, admission)
        )

    def test_cansubmitregistration_return_true_if_admission_state_accepted(self):
        admission = AdmissionFactory(state=ACCEPTED)
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, admission)
        )

    def test_cansubmitregistration_return_true_if_admission_state_draft_and_no_registration_required(self):
        admission = AdmissionFactory(state=DRAFT, formation__registration_required=False)
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, admission)
        )

    def test_cansubmitregistration_return_true_if_not_safe_methods(self):
        admission = AdmissionFactory(state=REGISTRATION_SUBMITTED)
        self.request.method = 'GET'
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, admission)
        )


class TestCanSendFiles(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.permission = CanSendFiles()
        cls.user = UserFactory()
        cls.request = APIRequestFactory(user=cls.user)

    def setUp(self):
        self.client.login(user=self.user)

    def test_cansendfiles_return_true_if_admission_state_is_accepted(self):
        admission = AdmissionFactory(state=ACCEPTED)
        file = AdmissionFileFactory(admission=admission)
        methods = ['POST', 'DELETE']
        for method in methods:
            self.request.method = method
            self.assertTrue(
                self.permission.has_object_permission(self.request, None, file)
            )

    def test_cansendfiles_return_true_if_admission_state_is_draft(self):
        admission = AdmissionFactory(state=DRAFT)
        file = AdmissionFileFactory(admission=admission)
        methods = ['POST', 'DELETE']
        for method in methods:
            self.request.method = method
            self.assertTrue(
                self.permission.has_object_permission(self.request, None, file)
            )

    def test_cansendfiles_return_true_if_safe_methods(self):
        admission = AdmissionFactory()
        file = AdmissionFileFactory(admission=admission)
        self.request.method = 'GET'
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, file)
        )

    def test_cansendfiles_return_false_with_wrong_state(self):
        states = [REJECTED, WAITING, SUBMITTED, REGISTRATION_SUBMITTED, VALIDATED]
        self.request.method = 'DELETE'
        for state in states:
            admission = AdmissionFactory(state=state)
            file = AdmissionFileFactory(admission=admission)
            self.assertFalse(
                self.permission.has_object_permission(self.request, None, file)
            )
        self.request.method = 'POST'
        for state in states:
            admission = AdmissionFactory(state=state)
            file = AdmissionFileFactory(admission=admission)
            self.assertFalse(
                self.permission.has_object_permission(self.request, None, file)
            )


class TestCanSubmitAdmission(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.permission = CanSubmitAdmission()
        cls.user = UserFactory()
        cls.request = APIRequestFactory(user=cls.user)
        cls.request.method = 'POST'

    def setUp(self):
        self.client.login(user=self.user)

    def test_cansubmitadmission_return_false_if_admission_state_not_draft(self):
        admission = AdmissionFactory(state=REJECTED)
        self.assertFalse(
            self.permission.has_object_permission(self.request, None, admission)
        )

    def test_cansubmitadmission_return_true_if_admission_state_draft(self):
        admission = AdmissionFactory(state=DRAFT)
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, admission)
        )

    def test_cansubmitregistration_return_true_if_not_safe_methods(self):
        admission = AdmissionFactory(state=DRAFT)
        self.request.method = 'GET'
        self.assertTrue(
            self.permission.has_object_permission(self.request, None, admission)
        )
