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
import uuid

from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from base.models.enums.entity_type import FACULTY
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from continuing_education.api.serializers.continuing_education_training import ContinuingEducationTrainingSerializer
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ContinuingEducationTrainingListTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:continuing-education-training-list')
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        edy = EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        EntityVersionFactory(entity=edy.management_entity, entity_type=FACULTY)
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group=cls.education_group)
        cls.training_manager = PersonFactory()
        PersonTraining(person=cls.training_manager, training=cls.continuing_education_training).save()

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['delete', 'put', 'patch', 'post']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_all_training_ensure_response_have_next_previous_results_count(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue('previous' in response.data)
        self.assertTrue('next' in response.data)
        self.assertTrue('results' in response.data)

        self.assertTrue('count' in response.data)
        expected_count = ContinuingEducationTraining.objects.all().count()
        self.assertEqual(response.data['count'], expected_count)

    def test_get_all_training_ensure_default_order(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = ContinuingEducationTraining.objects.all().order_by('education_group__educationgroupyear__acronym')
        serializer = ContinuingEducationTrainingSerializer(trainings, many=True, context={'request': RequestFactory().get(self.url)})
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_all_training_with_associated_training_managers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = ContinuingEducationTraining.objects.all().order_by('education_group__educationgroupyear__acronym')
        serializer = ContinuingEducationTrainingSerializer(trainings, many=True, context={'request': RequestFactory().get(self.url)})
        self.assertEqual(response.data['results'][0]['managers'], serializer.data[0]['managers'])


class ContinuingEducationTrainingDetailTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        edy = EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        EntityVersionFactory(entity=edy.management_entity, entity_type=FACULTY)
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group=cls.education_group)
        cls.user = UserFactory()
        cls.url = reverse(
            'continuing_education_api_v1:continuing-education-training-detail',
            kwargs={'uuid': cls.continuing_education_training.uuid}
        )
        cls.invalid_url = reverse(
            'continuing_education_api_v1:continuing-education-training-detail',
            kwargs={'uuid': uuid.uuid4()}
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_not_authorized(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method_not_allowed(self):
        methods_not_allowed = ['post', 'put', 'patch', 'delete']

        for method in methods_not_allowed:
            response = getattr(self.client, method)(self.url)
            self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_valid_continuing_education_training(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = ContinuingEducationTrainingSerializer(
            self.continuing_education_training,
            context={'request': RequestFactory().get(self.url)},
        )
        self.assertEqual(response.data, serializer.data)

    def test_get_invalid_continuing_education_training_case_not_found(self):
        response = self.client.get(self.invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FilterContinuingEducationTrainingTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.url = reverse('continuing_education_api_v1:continuing-education-training-list')
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        cls.education_group_year = EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        EntityVersionFactory(entity=cls.education_group_year.management_entity, entity_type=FACULTY)
        cls.continuing_education_training = ContinuingEducationTrainingFactory(education_group=cls.education_group)

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_continuing_education_training_case_filter_acronym_params(self):
        query_string = {'acronym': self.education_group_year.acronym}

        response = self.client.get(self.url, data=query_string)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        trainings = ContinuingEducationTraining.objects.filter(
            education_group__educationgroupyear__acronym=query_string['acronym']
        )

        serializer = ContinuingEducationTrainingSerializer(
            trainings,
            many=True,
            context={'request': RequestFactory().get(self.url, query_string)},
        )
        self.assertEqual(response.data['results'], serializer.data)
