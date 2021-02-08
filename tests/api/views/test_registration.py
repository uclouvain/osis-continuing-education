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
import random
import unittest
import uuid
from unittest import mock

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.registration import RegistrationListSerializer, \
    RegistrationDetailSerializer, \
    RegistrationPostSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, DRAFT, \
    REGISTRATION_SUBMITTED, VALIDATED
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class RegistrationListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

        CountryFactory(iso_code='NL')
        cls.person = ContinuingEducationPersonFactory()
        cls.address = AddressFactory()

        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.admission = AdmissionFactory(
            person_information=cls.person,
            address=cls.address,
            state=DRAFT,
            formation=cls.formation
        )

        cls.url = reverse('continuing_education_api_v1:registration-list', kwargs={'uuid': cls.person.uuid})

        for state in [VALIDATED, ACCEPTED, REGISTRATION_SUBMITTED]:
            cls.education_group = EducationGroupFactory()
            EducationGroupYearFactory(education_group=cls.education_group, academic_year=cls.academic_year)
            AdmissionFactory(
                person_information=cls.person,
                state=state,
                formation=ContinuingEducationTrainingFactory(
                    education_group=cls.education_group
                )
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'post', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_registration_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = Admission.registration_objects.count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_registration_ensure_default_order(self):
        """ This test ensure that default order is state [ASC Order] + formation [ASC Order]"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        registrations = Admission.registration_objects.all().order_by('state', 'formation')
        serializer = RegistrationListSerializer(registrations, many=True, context={'request': RequestFactory().get(self.url)})
        self.assertEqual(response.data['results'], serializer.data)

    @unittest.skip("formation and person_information ordering is not correct")
    def test_get_all_registration_specify_ordering_field(self):
        ordering_managed = ['state', 'formation__acronym', 'person_information__person__last_name']

        for order in ordering_managed:
            query_string = {api_settings.ORDERING_PARAM: order}
            response = self.client.get(self.url, kwargs=query_string)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            registrations = Admission.objects.all().order_by(order)
            serializer = RegistrationListSerializer(
                registrations,
                many=True,
                context={'request': RequestFactory().get(self.url, query_string)},
            )
            self.assertEqual(response.data['results'], serializer.data)


class RegistrationDetailUpdateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        GroupFactory(name='continuing_education_managers')
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        cls.user = UserFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.admission = AdmissionFactory(
            person_information=ContinuingEducationPersonFactory(person=PersonFactory(user=cls.user)),
            formation=ContinuingEducationTrainingFactory(
                education_group=cls.education_group
            ),
            state=random.choice([ACCEPTED, REGISTRATION_SUBMITTED, VALIDATED])
        )

        cls.url = reverse('continuing_education_api_v1:registration-detail-update', kwargs={'uuid': cls.admission.uuid})
        cls.invalid_url = reverse(
            'continuing_education_api_v1:registration-detail-update',
            kwargs={'uuid':  uuid.uuid4()}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_valid_registration(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = RegistrationDetailSerializer(
            self.admission,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_registration_case_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('continuing_education.business.admission.send_submission_email_to_admission_managers')
    def test_update_valid_registration(self, mock_mail):
        self.admission.state = ACCEPTED
        self.admission.save()
        self.assertEqual(1, Admission.registration_objects.all().count())
        data = {
            'vat_number': '123456',
            'id_card_number': '0000000',
            'use_address_for_billing': True,
            'use_address_for_post': True,
        }
        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = RegistrationPostSerializer(
            Admission.registration_objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.registration_objects.all().count())

    @mock.patch('continuing_education.business.admission.send_submission_email_to_admission_managers')
    def test_update_valid_registration_billing_address(self, mock_mail):
        self.admission.state = ACCEPTED
        self.admission.save()
        self.assertEqual(1, Admission.registration_objects.all().count())
        data = {
            'use_address_for_billing': False,
            'billing_address': {
                'location': 'PERDU'
            },
            'use_address_for_post': True
        }

        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = RegistrationPostSerializer(
            Admission.registration_objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.registration_objects.all().count())

    @mock.patch('continuing_education.business.admission.send_email')
    def test_registration_submit_email_notification(self, mock_send_email):
        self.admission.state = ACCEPTED
        self.admission.save()

        data = {
            'use_address_for_billing': False,
            'use_address_for_post': False,
            'state': REGISTRATION_SUBMITTED,
        }
        self.client.put(self.url, data=data)

        self.assertTrue(mock_send_email.called)

        mock_call_args_admin_notification = mock_send_email.call_args_list[0][1]
        self.assertEqual(
            mock_call_args_admin_notification.get('template_references').get('html'),
            'iufc_admin_admission_registr_submitted_html'
        )
        self.assertEqual(
            mock_call_args_admin_notification.get('connected_user'),
            self.user
        )

        mock_call_args_participant_notification = mock_send_email.call_args_list[1][1]
        self.assertEqual(
            mock_call_args_participant_notification.get('template_references').get('html'),
            'iufc_participant_admission_registr_submitted_html'
        )
        receivers = mock_call_args_participant_notification.get('receivers')
        self.assertCountEqual(
            [receiver.get('receiver_email') for receiver in receivers],
            [self.admission.email, self.admission.person_information.person.email]
        )
        self.assertEqual(
            mock_call_args_participant_notification.get('connected_user'),
            self.user
        )

    def test_update_invalid_registration(self):
        response = self.client.put(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
