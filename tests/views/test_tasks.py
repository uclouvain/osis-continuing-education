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

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import REGISTRATION_SUBMITTED, VALIDATED
from continuing_education.models.enums.groups import STUDENT_WORKERS_GROUP
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class ViewUpdateTasksTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.training_manager = ContinuingEducationTrainingManagerFactory()
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.registrations_to_validate = [
            AdmissionFactory(
                state=admission_state_choices.REGISTRATION_SUBMITTED,
                formation=cls.formation
            ) for _ in range(2)
        ]
        cls.registration_not_to_validate = AdmissionFactory(
            state=admission_state_choices.DRAFT,
            diploma_produced=True,
            formation=cls.formation
        )

        cls.diplomas_to_produce = [
            AdmissionFactory(
                state=admission_state_choices.VALIDATED,
                diploma_produced=False,
                formation=cls.formation,
                ucl_registration_complete=True,
                payment_complete=True,
                assessment_succeeded=True,
            ) for _ in range(2)
        ]
        cls.no_diploma_to_produce_because_waiting = AdmissionFactory(
            state=admission_state_choices.WAITING,
            diploma_produced=True,
            formation=cls.formation
        )

        cls.admissions_to_accept = [
            AdmissionFactory(
                state=random.choice([admission_state_choices.SUBMITTED, admission_state_choices.WAITING]),
                formation=cls.formation
            ) for _ in range(2)
            ]
        cls.admission_not_to_accept = AdmissionFactory(
            state=admission_state_choices.DRAFT,
            formation=cls.formation
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_list_tasks_html_content_for_iufc(self):
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tasks.html')
        self.assertTemplateUsed(response, 'fragment/tasks/registrations_to_validate.html')
        self.assertTemplateUsed(response, 'fragment/tasks/diplomas_to_produce.html')

    def test_list_tasks_html_content_for_manager(self):
        self.client.force_login(self.training_manager.person.user)
        response = self.client.get(reverse('list_tasks'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertTemplateUsed(response, 'tasks.html')
        self.assertTemplateUsed(response, 'fragment/tasks/admissions_to_accept.html')

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
        self.assertEqual(response.context['to_validate_count'], len(self.registrations_to_validate))

        self.assertNotIn(
            self.registration_not_to_validate,
            response.context['registrations_to_validate']
        )

        self.assertCountEqual(
            response.context['admissions_diploma_to_produce'],
            self.diplomas_to_produce
        )
        self.assertEqual(response.context['diplomas_count'], len(self.diplomas_to_produce))
        self.assertNotIn(
            self.no_diploma_to_produce_because_waiting,
            response.context['admissions_diploma_to_produce']
        )

        list_expected_waiting_and_submitted = self.admissions_to_accept
        list_expected_waiting_and_submitted.append(self.no_diploma_to_produce_because_waiting)

        self.assertCountEqual(
            response.context['admissions_to_accept'],
            list_expected_waiting_and_submitted
        )

        self.assertNotIn(
            self.admission_not_to_accept,
            response.context['admissions_to_accept']
        )

    def test_paper_registrations_file_received(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(registration.pk) for registration in self.registrations_to_validate]
        }
        response = self.client.post(reverse('paper_registrations_file_received'), data=post_data)

        for registration in self.registrations_to_validate:
            registration.refresh_from_db()
            self.assertTrue(registration.registration_file_received)

        self.assertRedirects(response, reverse('list_tasks'))

    def test_process_registrations_incorrect_state(self):
        reverses = ['paper_registrations_file_received']
        post_data = {
            "selected_registrations_to_validate":
                [str(self.registration_not_to_validate.pk)]
        }
        for reverse_name in reverses:
            response = self.client.post(reverse(reverse_name), data=post_data)

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
                [str(self.no_diploma_to_produce_because_waiting.pk)]
        }
        response = self.client.post(reverse('mark_diplomas_produced'), data=post_data)

        self.no_diploma_to_produce_because_waiting.refresh_from_db()
        self.assertEqual(self.no_diploma_to_produce_because_waiting.state, admission_state_choices.WAITING)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_process_admissions_denied(self):
        response = self.client.post(reverse('process_admissions'), data={})
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_process_admissions(self):
        post_data = {
            "selected_admissions_to_accept":
                [str(registration.pk) for registration in self.admissions_to_accept],
            "new_state": "Accepted"
        }
        self.client.force_login(self.training_manager.person.user)
        response = self.client.post(reverse('process_admissions'), data=post_data)
        for registration in self.admissions_to_accept:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.ACCEPTED)

        self.assertRedirects(response, reverse('list_tasks'))

    def test_process_admissions_incorrect_state(self):
        post_data = {
            "selected_admissions_to_accept":
                [str(self.admission_not_to_accept.pk)]
        }
        response = self.client.post(reverse('process_admissions'), data=post_data)

        self.admission_not_to_accept.refresh_from_db()
        self.assertEqual(self.admission_not_to_accept.state, admission_state_choices.DRAFT)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)


class UpdateTasksPermissionsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person_without_change_perm = PersonWithPermissionsFactory('view_admission')

        cls.registrations_to_validate = [
            AdmissionFactory(state=admission_state_choices.REGISTRATION_SUBMITTED) for _ in range(2)
        ]

        cls.diplomas_to_produce = [
            AdmissionFactory(state=admission_state_choices.VALIDATED, diploma_produced=False) for _ in range(2)
        ]

        cls.admissions_to_validate = [
            AdmissionFactory(state=admission_state_choices.SUBMITTED) for _ in range(2)
            ]

    def setUp(self):
        self.client.force_login(self.person_without_change_perm.user)

    def test_paper_registrations_file_received_without_permission(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(registration.pk) for registration in self.registrations_to_validate]
        }
        response = self.client.post(reverse('paper_registrations_file_received'), data=post_data)

        for registration in self.registrations_to_validate:
            registration.refresh_from_db()
            self.assertEqual(registration.state, admission_state_choices.REGISTRATION_SUBMITTED)

        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)

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

    def test_process_admissions_without_permission(self):
        post_data = {
            "selected_admissions_to_accept":
                [str(admission.pk) for admission in self.admissions_to_validate]
        }
        response = self.client.post(reverse('process_admissions'), data=post_data)

        for admission in self.admissions_to_validate:
            admission.refresh_from_db()
            self.assertEqual(admission.state, admission_state_choices.SUBMITTED)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)


class ViewTasksTrainingManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.training_manager = ContinuingEducationTrainingManagerFactory()
        cls.registration_to_validate = AdmissionFactory(
            formation=cls.formation,
            state=REGISTRATION_SUBMITTED,
        )
        cls.admission_diploma_to_produce = AdmissionFactory(
            formation=cls.formation,
            state=VALIDATED,
        )
        cls.admission_to_validate = AdmissionFactory(
            formation=cls.formation,
            state=admission_state_choices.SUBMITTED,
        )

    def setUp(self):
        self.client.force_login(self.training_manager.person.user)

    def test_paper_registrations_file_received_denied(self):
        post_data = {
            "selected_registrations_to_validate":
                [str(self.registration_to_validate.pk)]
        }
        response = self.client.post(
            reverse('paper_registrations_file_received'),
            data=post_data
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)


class ViewTasksStudentWorkerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        group = GroupFactory(name=STUDENT_WORKERS_GROUP)
        cls.student_worker = PersonFactory()
        cls.student_worker.user.groups.add(group)

        cls.admission_diploma_to_produce = AdmissionFactory(
            formation=cls.formation,
            state=VALIDATED,
        )
        cls.registration_to_validate = AdmissionFactory(
            formation=cls.formation,
            state=REGISTRATION_SUBMITTED,
        )

    def setUp(self):
        self.client.force_login(self.student_worker.user)

    def test_produce_diploma_denied(self):
        post_data = {
            "selected_diplomas_to_produce":
                [str(self.admission_diploma_to_produce.pk)]
        }
        response = self.client.post(
            reverse('mark_diplomas_produced'),
            data=post_data
        )
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
