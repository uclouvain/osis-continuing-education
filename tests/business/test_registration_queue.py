##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
from unittest import mock

from django.http import HttpResponseRedirect
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.user import UserFactory
from continuing_education.business.registration_queue import get_json_for_epc, format_address_for_json, \
    save_role_registered_in_admission, send_admission_to_queue, _gender_to_sex, MAX_LENGTH_FOR_STREET_FIELD_IN_EPC, \
    MAX_LENGTH_FOR_POSTAL_CODE_FIELD_IN_EPC, MAX_LENGTH_FOR_LOCALITY_FIELD_IN_EPC
from continuing_education.models.enums.admission_state_choices import VALIDATED
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_student_worker import \
    ContinuingEducationStudentWorkerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory
from continuing_education.views.common import UCL_REGISTRATION_REGISTERED, UCL_REGISTRATION_REJECTED, \
    UCL_REGISTRATION_STATE_CHANGED


class PrepareJSONTestCase(TestCase):
    def setUp(self):
        self.admission = AdmissionFactory()
        EducationGroupYearFactory(
            education_group=self.admission.formation.education_group,
            academic_year=create_current_academic_year()
        )

    def test_get_json_for_epc(self):
        result = get_json_for_epc(self.admission)
        expected_result = {
            'name': self.admission.person_information.person.last_name,
            'first_name': self.admission.person_information.person.first_name,
            'birth_date': self.admission.person_information.birth_date.strftime("%d/%m/%Y"),
            'birth_location': self.admission.person_information.birth_location,
            'birth_country_iso_code': self.admission.person_information.birth_country.iso_code,
            'sex': "M" if self.admission.person_information.person.gender == "H" else "F",
            'civil_state': self.admission.marital_status,
            'nationality_iso_code': self.admission.citizenship.iso_code,
            'mobile_number': self.admission.phone_mobile,
            'telephone_number': self.admission.residence_phone,
            'private_email': self.admission.email,
            'private_address': {
                'street': self.admission.address.location,
                'locality': self.admission.address.city,
                'postal_code': self.admission.address.postal_code,
                'country_name': self.admission.address.country.name,
                'country_iso_code': self.admission.address.country.iso_code
            },
            'staying_address': {
                'street': self.admission.residence_address.location,
                'locality': self.admission.residence_address.city,
                'postal_code': self.admission.residence_address.postal_code,
                'country_name': self.admission.residence_address.country.name,
                'country_iso_code': self.admission.residence_address.country.iso_code
            },
            'national_registry_number': self.admission.national_registry_number,
            'id_card_number': self.admission.id_card_number,
            'passport_number': self.admission.passport_number,
            'formation_code': self.admission.formation.acronym,
            'formation_academic_year': str(self.admission.academic_year.year),
            'student_case_uuid': str(self.admission.uuid)
        }
        self.assertDictEqual(result, expected_result)

    def test_get_json_for_epc_same_address(self):
        self.admission.residence_address = self.admission.address
        self.admission.save()
        result = get_json_for_epc(self.admission)
        expected_result = {
            'name': self.admission.person_information.person.last_name,
            'first_name': self.admission.person_information.person.first_name,
            'birth_date': self.admission.person_information.birth_date.strftime("%d/%m/%Y"),
            'birth_location': self.admission.person_information.birth_location,
            'birth_country_iso_code': self.admission.person_information.birth_country.iso_code,
            'sex': "M" if self.admission.person_information.person.gender == "H" else "F",
            'civil_state': self.admission.marital_status,
            'nationality_iso_code': self.admission.citizenship.iso_code,
            'mobile_number': self.admission.phone_mobile,
            'telephone_number': self.admission.residence_phone,
            'private_email': self.admission.email,
            'private_address': {
                'street': self.admission.address.location,
                'locality': self.admission.address.city,
                'postal_code': self.admission.address.postal_code,
                'country_name': self.admission.address.country.name,
                'country_iso_code': self.admission.address.country.iso_code
            },
            'staying_address': {},
            'national_registry_number': self.admission.national_registry_number,
            'id_card_number': self.admission.id_card_number,
            'passport_number': self.admission.passport_number,
            'formation_code': self.admission.formation.acronym,
            'formation_academic_year': str(self.admission.academic_year.year),
            'student_case_uuid': str(self.admission.uuid)
        }
        self.assertDictEqual(result, expected_result)

    def test_format_address_for_json(self):
        result = format_address_for_json(self.admission.address)
        expected_result = {
            'street': self.admission.address.location,
            'locality': self.admission.address.city,
            'postal_code': self.admission.address.postal_code,
            'country_name': self.admission.address.country.name,
            'country_iso_code': self.admission.address.country.iso_code
        }
        self.assertDictEqual(result, expected_result)

    def test_format_address_for_json_if_no_address(self):
        result = format_address_for_json(None)
        expected_result = {
            'street': '',
            'locality': '',
            'postal_code': '',
            'country_name': '',
            'country_iso_code': ''
        }
        self.assertDictEqual(result, expected_result)

    def test_format_address_for_json_if_no_country(self):
        self.admission.address.country = None
        self.admission.address.save()
        result = format_address_for_json(self.admission.address)
        expected_result = {
            'street': self.admission.address.location,
            'locality': self.admission.address.city,
            'postal_code': self.admission.address.postal_code,
            'country_name': '',
            'country_iso_code': ''
        }
        self.assertDictEqual(result, expected_result)

    def test_format_address_for_json_if_address_fields_too_long(self):
        address_with_too_long_fields = AddressFactory(
            location='Rue du nom plus long que le nombre de 50 caractères autorisés',
            postal_code='01234567890123456',
            city='Rue du ville plus long que le nombre de 40 caractères autorisés',
        )
        result = format_address_for_json(address_with_too_long_fields)
        self.assertEqual(
            result.get('street'),
            address_with_too_long_fields.location[0:MAX_LENGTH_FOR_STREET_FIELD_IN_EPC]
        )
        self.assertEqual(
            result.get('locality'),
            address_with_too_long_fields.city[0:MAX_LENGTH_FOR_LOCALITY_FIELD_IN_EPC]
        )
        self.assertEqual(
            result.get('postal_code'),
            address_with_too_long_fields.postal_code[0:MAX_LENGTH_FOR_POSTAL_CODE_FIELD_IN_EPC]
        )


class SaveRoleRegisteredTestCase(TestCase):
    def setUp(self):
        self.admission = AdmissionFactory()
        self.basic_response = {
            'message': 'IUFC_NO_ERROR',
            'success': True,
            'student_case_uuid': str(self.admission.uuid),
            'registration_id': '123456789',
            'registration_status': 'INSCRIT'
        }

    @mock.patch('continuing_education.business.registration_queue.get_revision_messages', return_value='')
    def test_save_role_registered_in_admission_if_queue_success(self, mock_get):
        data = json.dumps(self.basic_response).encode('utf-8')
        save_role_registered_in_admission(data)
        mock_get.assert_called_once_with(UCL_REGISTRATION_REGISTERED)
        self.admission.refresh_from_db()
        self.assertEqual(self.admission.ucl_registration_complete, UCLRegistrationState.INSCRIT.name)
        self.assertEqual(self.admission.noma, '123456789')

    @mock.patch('continuing_education.business.registration_queue.get_revision_messages', return_value='')
    def test_save_role_registered_in_admission_if_queue_success_and_other_statut(self, mock_get):
        self.basic_response['registration_status'] = 'DECES'
        data = json.dumps(self.basic_response).encode('utf-8')
        save_role_registered_in_admission(data)
        mock_get.assert_called_once_with(UCL_REGISTRATION_STATE_CHANGED)
        self.admission.refresh_from_db()
        self.assertEqual(self.admission.ucl_registration_complete, UCLRegistrationState.DECES.name)
        self.assertEqual(self.admission.noma, '123456789')

    @mock.patch('continuing_education.business.registration_queue.get_revision_messages', return_value='')
    def test_save_role_registered_in_admission_no_change_if_queue_fail(self, mock_get):
        self.basic_response['success'] = False
        data = json.dumps(self.basic_response).encode('utf-8')
        save_role_registered_in_admission(data)
        self.admission.refresh_from_db()
        mock_get.assert_called_once_with(UCL_REGISTRATION_REJECTED)
        self.assertEqual(self.admission.ucl_registration_complete, UCLRegistrationState.REJECTED.name)
        self.assertEqual(self.admission.ucl_registration_error, self.basic_response['message'])


@override_settings(
    QUEUES={
        'QUEUE_USER': 'USER',
        'QUEUE_PASSWORD': 'PASSWORD',
        'QUEUE_URL': 'URL',
        'QUEUE_PORT': 0000,
        'QUEUE_CONTEXT_ROOT': 'CONTEXT_ROOT',
        'QUEUES_NAME': {
            'IUFC_TO_EPC': 'NAME'
        }
    }
)
class SendAdmissionToQueueTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admission = AdmissionFactory()
        EducationGroupYearFactory(
            education_group=cls.admission.formation.education_group,
            academic_year=create_current_academic_year()
        )

    @mock.patch('continuing_education.business.registration_queue.pika.BlockingConnection')
    @mock.patch('continuing_education.business.registration_queue.send_message')
    def test_send_admission_to_queue(self, mock_send, mock_pika):
        request = RequestFactory()
        request.user = UserFactory()
        send_admission_to_queue(request, self.admission)
        self.assertTrue(mock_pika.called)
        self.assertTrue(mock_send.called)
        self.assertEqual('NAME', mock_send.call_args_list[0][0][0])
        self.assertEqual(get_json_for_epc(self.admission), mock_send.call_args_list[0][0][1])
        self.assertEqual(self.admission.ucl_registration_complete, UCLRegistrationState.SENDED.name)


@override_settings(
    QUEUES={
        'QUEUE_USER': 'USER',
        'QUEUE_PASSWORD': 'PASSWORD',
        'QUEUE_URL': 'URL',
        'QUEUE_PORT': 0000,
        'QUEUE_CONTEXT_ROOT': 'CONTEXT_ROOT',
        'QUEUES_NAME': {
            'IUFC_TO_EPC': 'NAME'
        }
    }
)
class SendingAdmissionViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.continuing_education_manager = ContinuingEducationManagerFactory()
        cls.admission = AdmissionFactory(state=VALIDATED)
        EducationGroupYearFactory(
            education_group=cls.admission.formation.education_group,
            academic_year=create_current_academic_year()
        )
        cls.url = reverse('injection_to_epc', args=[cls.admission.pk])

    def setUp(self):
        self.client.force_login(self.continuing_education_manager.person.user)

    @mock.patch('continuing_education.business.registration_queue.pika.BlockingConnection')
    @mock.patch('continuing_education.business.registration_queue.send_message')
    def test_inject_admission_to_epc(self, mock_send, mock_pika):
        response = self.client.get(self.url)
        self.assertEqual(HttpResponseRedirect.status_code, response.status_code)
        self.admission.refresh_from_db()
        self.assertEqual(UCLRegistrationState.SENDED.name, self.admission.ucl_registration_complete)
        self.assertTrue(mock_send.called)
        self.assertEqual('NAME', mock_send.call_args_list[0][0][0])

    def test_inject_admission_to_epc_unlogged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_inject_admission_to_epc_refused_to_training_manager(self):
        continuing_education_training_manager = ContinuingEducationTrainingManagerFactory()
        self.client.force_login(continuing_education_training_manager.person.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_inject_admission_to_epc_refused_to_student_worker(self):
        student_worker = ContinuingEducationStudentWorkerFactory()
        self.client.force_login(student_worker.person.user)
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_gender_to_sex(self):
        self.assertEqual(
            _gender_to_sex("H"), "M"
        )
        self.assertEqual(
            _gender_to_sex("F"), "F"
        )
        with self.assertRaises(ValueError):
            _gender_to_sex("X")
