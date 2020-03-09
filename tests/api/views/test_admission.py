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
import datetime
import uuid
from unittest import mock

from django.forms import model_to_dict
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums.entity_type import FACULTY
from base.models.person import Person
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.admission import AdmissionListSerializer, AdmissionDetailSerializer, \
    AdmissionPostSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import SUBMITTED, ACCEPTED, REJECTED, DRAFT, WAITING, \
    VALIDATED
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class AdmissionListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

        cls.person = ContinuingEducationPersonFactory()
        cls.address = AddressFactory()
        cls.academic_year = AcademicYearFactory(year=2018)

        cls.url = reverse('continuing_education_api_v1:admission-list', kwargs={'uuid': cls.person.uuid})

        for state in [SUBMITTED, ACCEPTED, REJECTED, DRAFT]:
            education_group = EducationGroupFactory()
            edy = EducationGroupYearFactory(
                education_group=education_group,
                academic_year=cls.academic_year
            )
            EntityVersionFactory(entity=edy.management_entity, entity_type=FACULTY)
            cls.formation = ContinuingEducationTrainingFactory(education_group=education_group)
            cls.admission = AdmissionFactory(
                person_information=cls.person,
                address=cls.address,
                state=state,
                formation=cls.formation
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

    def test_get_all_admission_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = Admission.objects.all().exclude(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED
        ]).count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_admission_ensure_default_order(self):
        """ This test ensure that default order is state [ASC Order] + formation [ASC Order]"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        admissions = Admission.objects.all().exclude(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED
        ]).order_by('state')
        serializer = AdmissionListSerializer(admissions, many=True, context={'request': RequestFactory().get(self.url)})
        self.assertEqual(response.data['results'], serializer.data)


class AdmissionCreateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.citizenship = CountryFactory(iso_code='FR')
        new_country = CountryFactory(iso_code='NL')
        cls.person = ContinuingEducationPersonFactory(birth_country=cls.citizenship)
        cls.address = AddressFactory()
        cls.academic_year = AcademicYearFactory(year=2018)

        cls.url = reverse('continuing_education_api_v1:admission-create')

        for state in [SUBMITTED, ACCEPTED, REJECTED, DRAFT]:
            education_group = EducationGroupFactory()
            EducationGroupYearFactory(
                education_group=education_group,
                academic_year=cls.academic_year
            )
            cls.formation = ContinuingEducationTrainingFactory(education_group=education_group)
            cls.admission = AdmissionFactory(
                citizenship=cls.citizenship,
                person_information=cls.person,
                address=cls.address,
                state=state,
                formation=cls.formation
            )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_create_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'get', 'patch']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_valid_admission_with_existing_person(self):
        self.assertEqual(3, Admission.admission_objects.all().count())
        self.assertEqual(1, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(1, Person.objects.all().count())
        person_information = self.admission.person_information
        data = {
            'first_name': person_information.person.first_name,
            'last_name': person_information.person.last_name,
            'gender': person_information.person.gender,
            'email': person_information.person.email,
            'birth_location': person_information.birth_location,
            'birth_date': person_information.birth_date,
            'birth_country': person_information.birth_country.iso_code,
            'admission_email': 'a@c.dk',
            'formation': self.formation.uuid
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(4, Admission.admission_objects.all().count())
        self.assertEqual(1, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(1, Person.objects.all().count())

    def test_create_valid_admission_with_new_person_and_person_info(self):
        self.assertEqual(3, Admission.admission_objects.all().count())
        self.assertEqual(1, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(1, Person.objects.all().count())

        p = PersonFactory(email='b@d.be')
        ContinuingEducationPersonFactory(person=p)
        data = {
            'birth_date': datetime.date.today(),
            'birth_country':  'NL',
            'birth_location': 'Turlututu',
            'first_name': 'Benjamin',
            'last_name': 'Dau',
            'gender': 'M',
            'email': 'b@d.be',
            'admission_email': 'a@c.dk',
            'formation': self.formation.uuid
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(4, Admission.admission_objects.all().count())
        self.assertEqual(2, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(2, Person.objects.all().count())

    def test_create_admission_missing_formation(self):
        data = {
            'person_information': {
                'person': {
                    'uuid': self.person.person.uuid
                }
            },
            'email': 'a@c.dk',
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_admission_missing_person(self):
        data = {
            'email': 'a@c.dk',
            'formation': model_to_dict(self.formation)
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_admission(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AdmissionDetailUpdateTestCase(APITestCase):
    def setUp(self):
        GroupFactory(name='continuing_education_managers')
        self.citizenship = CountryFactory()
        self.user = UserFactory()
        self.academic_year = AcademicYearFactory(year=2018)
        education_group = EducationGroupFactory()
        edy = EducationGroupYearFactory(
            education_group=education_group,
            academic_year=self.academic_year
        )
        EntityVersionFactory(entity=edy.management_entity, entity_type=FACULTY)
        self.admission = AdmissionFactory(
            citizenship=self.citizenship,
            person_information=ContinuingEducationPersonFactory(person=PersonFactory(user=self.user)),
            formation=ContinuingEducationTrainingFactory(education_group=education_group),
            state=DRAFT
        )

        self.url = reverse('continuing_education_api_v1:admission-detail-update', kwargs={'uuid': self.admission.uuid})
        self.invalid_url = reverse(
            'continuing_education_api_v1:admission-detail-update',
            kwargs={'uuid':  uuid.uuid4()}
        )

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

    def test_get_valid_admission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionDetailSerializer(
            self.admission,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_admission_case_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_valid_admission(self):
        data = {
            'email': 'aaa@ddd.cd',
            'phone_mobile': '0000',
        }

        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionPostSerializer(
            Admission.objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.objects.all().count())

    @mock.patch('continuing_education.business.admission.send_email')
    def test_submit_admission_mail_notification(self, mock_send_email):
        data = {
            'state': SUBMITTED,
        }
        self.client.patch(self.url, data=data)

        self.assertTrue(mock_send_email.called)

        mock_call_args_admin_notification = mock_send_email.call_args_list[0][1]
        self.assertEqual(
            mock_call_args_admin_notification.get('template_references').get('html'),
            'iufc_admin_admission_submitted_html'
        )
        self.assertEqual(
            mock_call_args_admin_notification.get('connected_user'),
            self.user
        )

        mock_call_args_participant_notification = mock_send_email.call_args_list[1][1]
        self.assertEqual(
            mock_call_args_participant_notification.get('template_references').get('html'),
            'iufc_participant_admission_submitted_html'
        )
        self.assertEqual(
            mock_call_args_participant_notification.get('receivers')[0].get('receiver_email'),
            self.admission.person_information.person.email
        )
        self.assertEqual(
            mock_call_args_participant_notification.get('connected_user'),
            self.user
        )

    @mock.patch('continuing_education.business.admission.send_email')
    def test_edit_admission_state_mail_notification(self, mock_send_email):
        new_statuses = [ACCEPTED, REJECTED, WAITING, VALIDATED]

        for new_status in new_statuses:
            with self.subTest(new_status=new_status):
                data = {
                    'state': new_status,
                }
                self.client.patch(self.url, data=data)

                self.assertTrue(mock_send_email.called)
                mock_call_args = mock_send_email.call_args[1]
                self.assertEqual(
                    mock_call_args.get('template_references').get('html'),
                    'iufc_participant_state_changed_accepted_html'
                )
                self.assertEqual(
                    mock_call_args.get('receivers')[0].get('receiver_email'),
                    self.admission.person_information.person.email
                )
                self.assertEqual(
                    mock_call_args.get('connected_user'),
                    self.user
                )

    @mock.patch('continuing_education.business.admission.send_submission_email_to_admission_managers')
    def test_update_valid_admission_address(self, mock_mail):
        data = {
            'main_address': {
                'location': 'PERDU'
            }
        }

        response = self.client.patch(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionPostSerializer(
            Admission.objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.objects.all().count())

    def test_update_invalid_admission(self):
        response = self.client.put(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
