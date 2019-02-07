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
import datetime
import unittest
import uuid

from django.forms import model_to_dict
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.models.person import Person
from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.admission import AdmissionListSerializer, AdmissionDetailSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums.admission_state_choices import SUBMITTED, ACCEPTED, REJECTED, DRAFT
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class AdmissionListCreateTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:admission-list-create')

        cls.citizenship = CountryFactory(iso_code='FR')
        new_country = CountryFactory(iso_code='NL')
        cls.person = ContinuingEducationPersonFactory(
            birth_country=cls.citizenship
        )
        cls.address = AddressFactory()
        cls.formation = TrainingFactory()
        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=cls.person,
            address=cls.address,
            state=DRAFT,
            formation=cls.formation
        )
        AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=ContinuingEducationPersonFactory(),
            state=SUBMITTED,
            formation=TrainingFactory()
        )
        AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=ContinuingEducationPersonFactory(),
            state=ACCEPTED,
            formation=TrainingFactory()
        )
        AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=ContinuingEducationPersonFactory(),
            state=REJECTED,
            formation=TrainingFactory()
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put']

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
        expected_count = Admission.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_admission_ensure_default_order(self):
        """ This test ensure that default order is state [ASC Order] + formation [ASC Order]"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        admissions = Admission.objects.all().order_by('state', 'formation')
        serializer = AdmissionListSerializer(admissions, many=True, context={'request': RequestFactory().get(self.url)})
        self.assertEqual(response.data['results'], serializer.data)

    @unittest.skip("formation and person_information ordering is not correct")
    def test_get_all_admission_specify_ordering_field(self):
        ordering_managed = ['state', 'formation__acronym', 'person_information__person__last_name']

        for order in ordering_managed:
            query_string = {api_settings.ORDERING_PARAM: order}
            response = self.client.get(self.url, kwargs=query_string)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            admissions = Admission.objects.all().order_by(order)
            serializer = AdmissionListSerializer(
                admissions,
                many=True,
                context={'request': RequestFactory().get(self.url, query_string)},
            )
            self.assertEqual(response.data['results'], serializer.data)

    def test_create_valid_admission_with_existing_person(self):
        self.assertEqual(4, Admission.objects.all().count())
        self.assertEqual(4, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(4, Person.objects.all().count())
        data = {
            'person_information': {
                'uuid': self.admission.person_information.uuid,
                'person': {
                    'uuid': self.admission.person_information.person.uuid
                },
                'birth_country': self.admission.person_information.birth_country.iso_code

            },
            'email': 'a@c.dk',
            'formation': {
                'code': self.formation.partial_acronym,
                'education_group_type': self.formation.education_group_type.name,
                'academic_year': self.formation.academic_year.year,
                'acronym': self.formation.acronym,
                'title': self.formation.title
            }
        }

        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(5, Admission.objects.all().count())
        self.assertEqual(4, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(4, Person.objects.all().count())

    def test_create_valid_admission_with_new_person_and_person_info(self):
        self.assertEqual(4, Admission.objects.all().count())
        self.assertEqual(4, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(4, Person.objects.all().count())
        data = {
            'person_information': {
                'birth_date': datetime.date.today(),
                'birth_country':  'NL',
                'birth_location': 'Turlututu',
                'person': {
                    'first_name': 'Benjamin',
                    'last_name': 'Dau',
                    'gender': 'M',
                    'email': 'b@d.be'
                },
            },
            'email': 'a@c.dk',
            'formation': model_to_dict(self.formation)
        }
        data['formation']['code'] = self.formation.partial_acronym
        data['formation']['education_group_type'] = self.formation.education_group_type.name
        data['formation']['academic_year'] = self.formation.academic_year.year
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(5, Admission.objects.all().count())
        self.assertEqual(5, ContinuingEducationPerson.objects.all().count())
        self.assertEqual(5, Person.objects.all().count())

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


class AdmissionDetailUpdateDestroyTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.citizenship = CountryFactory()

        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=ContinuingEducationPersonFactory(),
            formation=TrainingFactory()
        )

        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:admission-detail-update-destroy', kwargs={'uuid': cls.admission.uuid})
        cls.invalid_url = reverse(
            'continuing_education_api_v1:admission-detail-update-destroy',
            kwargs={'uuid':  uuid.uuid4()}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post']

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

    def test_delete_valid_admission(self):
        self.assertEqual(1, Admission.objects.all().count())
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(0, Admission.objects.all().count())

    def test_delete_invalid_admission_case_not_found(self):
        response = self.client.delete(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_valid_admission(self):
        self.assertEqual(1, Admission.objects.all().count())
        data = {
            'email': 'aaa@ddd.cd',
            'phone_mobile': '0000',
        }

        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionDetailSerializer(
            Admission.objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.objects.all().count())

    def test_update_valid_admission_address(self):
        self.assertEqual(1, Admission.objects.all().count())
        data = {
            'main_address': {
                'location': 'PERDU'
            }
        }

        response = self.client.put(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = AdmissionDetailSerializer(
            Admission.objects.all().first(),
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(1, Admission.objects.all().count())

    def test_update_invalid_admission(self):
        response = self.client.put(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
