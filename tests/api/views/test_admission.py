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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.settings import api_settings
from rest_framework.test import APITestCase

from base.tests.factories.education_group_year import TrainingFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.admission import AdmissionListSerializer, AdmissionDetailSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import SUBMITTED, ACCEPTED, REJECTED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory


class GetAllAdmissionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:admission-list')

        cls.citizenship = CountryFactory()

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

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

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

    def test_get_all_admission_specify_ordering_field(self):
        ordering_managed = ['formation', 'state', 'person_information']

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
            print(serializer.data)
            print(response.data['results'])
            self.assertEqual(response.data['results'], serializer.data)


class GetAdmissionTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.citizenship = CountryFactory()

        cls.admission = AdmissionFactory(
            citizenship=cls.citizenship,
            person_information=ContinuingEducationPersonFactory(),
            formation=TrainingFactory()
        )

        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:admission-detail', kwargs={'uuid': cls.admission.uuid})

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'delete', 'put']

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
        invalid_url = reverse('continuing_education_api_v1:admission-detail', kwargs={'uuid':  uuid.uuid4()})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
