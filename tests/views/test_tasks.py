##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseForbidden
from django.test import TestCase

from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.enums import admission_state_choices
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ViewUpdateTasksTestCase(TestCase):
    def setUp(self):
        group = GroupFactory(name='continuing_education_managers')
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.manager.user.groups.add(group)
        self.client.force_login(self.manager.user)
        self.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.registrations_to_validate = [
            AdmissionFactory(
                state=admission_state_choices.REGISTRATION_SUBMITTED,
                formation=self.formation
            ) for _ in range(2)
        ]
        self.registration_not_to_validate = AdmissionFactory(
            state=admission_state_choices.DRAFT,
            diploma_produced=True,
            formation=self.formation
        )

        self.diplomas_to_produce = [
            AdmissionFactory(
                state=admission_state_choices.VALIDATED,
                diploma_produced=False,
                formation=self.formation
            ) for _ in range(2)
        ]
        self.no_diploma_to_produce = AdmissionFactory(
            state=admission_state_choices.WAITING,
            diploma_produced=True,
            formation=self.formation
        )

    def test_list_tasks(self):
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tasks.html')
        self.assertTemplateUsed(response, 'fragment/tasks/registrations_to_validate.html')
        self.assertTemplateUsed(response, 'fragment/tasks/diplomas_to_produce.html')

        self.assertCountEqual(
            response.context['registrations_to_validate'],
            self.registrations_to_validate
        )

        self.assertNotIn(
            self.registration_not_to_validate,
            response.context['registrations_to_validate']
        )

        self.assertCountEqual(
            response.context['admissions_diploma_to_produce'],
            self.diplomas_to_produce
        )
        self.assertNotIn(
            self.no_diploma_to_produce,
            response.context['admissions_diploma_to_produce']
        )

    def test_validate_registrations(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(registration.pk) for registration in self.registrations_to_validate]
        }
        response = self.client.post(reverse('validate_registrations'), data=post_data)

        for registration in self.registrations_to_validate:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.VALIDATED)

        self.assertRedirects(response, reverse('list_tasks'))

    def test_validate_registrations_incorrect_state(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(self.registration_not_to_validate.pk)]
        }
        response = self.client.post(reverse('validate_registrations'), data=post_data)

        self.registration_not_to_validate.refresh_from_db()
        self.assertEqual(self.registration_not_to_validate.state, admission_state_choices.DRAFT)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_mark_diplomas_produced(self):
        post_data = {
            "selected_diplomas_to_produce":
                [str(registration.pk) for registration in self.diplomas_to_produce]
        }
        response = self.client.post(reverse('mark_diplomas_produced'), data=post_data)

        for registration in self.diplomas_to_produce:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.VALIDATED)
            self.assertEqual(registration.diploma_produced, True)

        self.assertRedirects(response, reverse('list_tasks') + '#diploma_to_produce')

    def test_mark_diplomas_produced_incorrect_state(self):
        post_data = {
            "selected_diplomas_to_produce":
                [str(self.no_diploma_to_produce.pk)]
        }
        response = self.client.post(reverse('mark_diplomas_produced'), data=post_data)

        self.no_diploma_to_produce.refresh_from_db()
        self.assertEqual(self.no_diploma_to_produce.state, admission_state_choices.WAITING)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)


class UpdateTasksPermissionsTestCase(TestCase):
    def setUp(self):
        person_without_change_perm = PersonWithPermissionsFactory('can_access_admission')
        self.client.force_login(person_without_change_perm.user)

        self.registrations_to_validate = [
            AdmissionFactory(state=admission_state_choices.REGISTRATION_SUBMITTED) for _ in range(2)
        ]

        self.diplomas_to_produce = [
            AdmissionFactory(state=admission_state_choices.VALIDATED, diploma_produced=False) for _ in range(2)
        ]

    def test_validate_registrations_without_permission(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(registration.pk) for registration in self.registrations_to_validate]
        }
        response = self.client.post(reverse('validate_registrations'), data=post_data)

        for registration in self.registrations_to_validate:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.REGISTRATION_SUBMITTED)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_mark_diplomas_produced_without_permission(self):
        post_data = {
            "selected_diplomas_to_produce":
                [str(registration.pk) for registration in self.diplomas_to_produce]
        }
        response = self.client.post(reverse('mark_diplomas_produced'), data=post_data)

        for registration in self.diplomas_to_produce:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.VALIDATED)
            self.assertEqual(registration.diploma_produced, False)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
