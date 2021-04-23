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
from django.contrib import messages
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.auth.roles.continuing_education_training_manager import ContinuingEducationTrainingManager
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class ManagerListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.manager.person.employee = True
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year,
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group,
            active=True
        )
        cls.training_manager = ContinuingEducationTrainingManagerFactory(training=cls.formation)

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_managers_list(self):
        response = self.client.get(reverse('list_managers'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertEqual(response.context['managers'].object_list, [self.training_manager.person])
        self.assertTemplateUsed(response, 'managers.html')

    def test_assign_manager_to_training(self):
        employee = PersonFactory(employee=True)
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 1)
        data = {
            'training': self.formation.pk,
            'person': employee.pk
        }
        response = self.client.post(reverse('add_continuing_education_training_manager'), data=data)
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 2)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

        messages_list = list(messages.get_messages(response.wsgi_request))
        success_msg = gettext('Successfully assigned %(manager)s to the training %(training)s') % {
            "manager": employee,
            "training": self.formation.acronym
        }
        self.assertIn(success_msg, str(messages_list[0]))
        self.assertEqual(list(employee.user.groups.values_list('name', flat=True)), [self.training_manager.group_name])

    def test_add_employee_to_training_managers_group(self):
        employee = PersonFactory(employee=True)
        self.assertEqual(list(employee.user.groups.all()), [])
        data = {
            'training': self.formation.pk,
            'person': employee.pk
        }
        response = self.client.post(reverse('add_continuing_education_training_manager'), data=data)
        self.assertEqual(list(employee.user.groups.values_list('name', flat=True)), [self.training_manager.group_name])
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

    def test_manager_already_assigned_to_training(self):
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 1)
        data = {
            'training': self.formation.pk,
            'person': self.training_manager.person.pk
        }
        response = self.client.post(reverse('add_continuing_education_training_manager'), data)
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 1)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            gettext("Manager is already assigned on this training"),
            str(messages_list[0])
        )

    def test_manager_person_with_no_user(self):
        employee = PersonFactory(employee=True, user=None)
        training = ContinuingEducationTrainingFactory()
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=training).count(), 0)
        data = {
            'training': self.formation.pk,
            'person': employee.pk
        }
        response = self.client.post(reverse('add_continuing_education_training_manager'), data)
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=training).count(), 0)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertIn(
            gettext("Manager person has no user"),
            str(messages_list[0])
        )

    def test_desassign_manager_from_training(self):
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 1)
        args = [
            self.formation.pk,
            self.training_manager.person.pk
        ]
        response = self.client.get(reverse('delete_continuing_education_training_manager', args=args))
        self.assertEqual(ContinuingEducationTrainingManager.objects.filter(training=self.formation).count(), 0)
        messages_list = list(messages.get_messages(response.wsgi_request))
        success_msg = gettext('Successfully desassigned %(manager)s from the training %(training)s') % {
            "manager": self.training_manager.person,
            "training": self.formation.acronym
        }
        self.assertIn(success_msg, str(messages_list[0]))


class ViewManagerCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()

    def setUp(self):
        self.client.force_login(self.manager.person.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('list_managers'), data={
            'training': 1,
        })
        cached_response = self.client.get(reverse('list_managers'))
        self.assertEqual(response.wsgi_request.GET['training'], cached_response.wsgi_request.GET['training'])
