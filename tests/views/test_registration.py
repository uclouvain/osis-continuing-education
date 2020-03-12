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
from unittest.mock import patch

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import status

from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.registration import RegistrationForm, \
    UN_UPDATABLE_FIELDS_FOR_CONTINUING_EDUCATION_TRAINING_MGR
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED
from continuing_education.models.enums.groups import STUDENT_WORKERS_GROUP, MANAGERS_GROUP, TRAINING_MANAGERS_GROUP
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ViewRegistrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission', groups=[MANAGERS_GROUP])
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.admission_accepted = AdmissionFactory(
            state=admission_state_choices.ACCEPTED,
            formation=cls.formation
        )
        cls.admission_rejected = AdmissionFactory(
            state=admission_state_choices.REJECTED,
            formation=cls.formation
        )
        cls.admission_validated = AdmissionFactory(
            state=admission_state_choices.VALIDATED,
            formation=cls.formation
        )

    def setUp(self):
        self.client.force_login(self.manager.user)

    def test_list_registrations(self):
        url = reverse('registration')
        response = self.client.get(url)
        admissions = response.context['admissions']
        for admission in admissions:
            self.assertEqual(admission.state, admission_state_choices.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registrations.html')

    def test_list_registrations_pagination_empty_page(self):
        url = reverse('registration')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registrations.html')

    def test_registration_edit_not_found(self):
        response = self.client.get(reverse('registration_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_edit_get_registration_found(self):
        url = reverse('registration_edit', args=[self.admission_accepted.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration_form.html')

    def test_edit_post_registration_found(self):
        admission = AdmissionFactory(formation=self.formation)
        admission_dict = model_to_dict(admission)
        admission_dict['billing_address'] = admission.billing_address
        admission_dict['residence_address'] = admission.residence_address
        admission_dict['citizenship'] = admission.citizenship
        admission_dict['address'] = admission.address
        url = reverse('registration_edit', args=[self.admission_accepted.id])
        form = RegistrationForm(admission_dict)
        form.is_valid()
        response = self.client.post(url, data=form.cleaned_data)
        self.assertRedirects(
            response,
            reverse('admission_detail', args=[self.admission_accepted.id]) + "#registration"
        )
        self.admission_accepted.refresh_from_db()

        # verifying that fields are correctly updated
        for key in form.cleaned_data.keys():
            field_value = self.admission_accepted.__getattribute__(key)
            if key not in UN_UPDATABLE_FIELDS_FOR_CONTINUING_EDUCATION_TRAINING_MGR:
                self.assertEqual(field_value, admission_dict[key])

    def test_registration_list_unauthorized(self):
        self.client.force_login(_build_unauthorized_user())
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_detail_unauthorized(self):
        self.client.force_login(_build_unauthorized_user())
        url = reverse('admission_detail', kwargs={'admission_id': self.admission_accepted.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_edit_unauthorized(self):
        self.client.force_login(_build_unauthorized_user())
        url = reverse('registration_edit', kwargs={'admission_id': self.admission_accepted.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_cancellations(self):
        url = reverse('cancelled_files')
        response = self.client.get(url)
        admissions = response.context['admissions']
        for admission in admissions:
            self.assertEqual(admission.state, admission_state_choices.CANCELLED)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cancellations.html')

    def test_list_cancellations_pagination_empty_page(self):
        url = reverse('cancelled_files')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cancellations.html')

    def test_registration_list_unauthorized_cancelled_files(self):
        self.client.force_login(_build_unauthorized_user())
        url = reverse('cancelled_files')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RegistrationStateChangedTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.faculty_manager = PersonWithPermissionsFactory(
            'can_access_admission',
            'change_admission',
        )
        cls.formation = ContinuingEducationTrainingFactory(education_group=cls.education_group)
        PersonTraining(person=cls.faculty_manager, training=cls.formation).save()
        training_manager_group = GroupFactory(name=TRAINING_MANAGERS_GROUP)
        cls.faculty_manager.user.groups.add(training_manager_group)
        group = GroupFactory(name=MANAGERS_GROUP)
        cls.continuing_education_manager = PersonWithPermissionsFactory(
            'can_access_admission',
            'change_admission',
            'can_validate_registration'
        )
        cls.continuing_education_manager.user.groups.add(group)
        EntityVersionFactory(
            entity=cls.formation.management_entity
        )
        cls.registration_submitted = AdmissionFactory(
            formation=cls.formation,
            state=REGISTRATION_SUBMITTED,
            academic_year=cls.academic_year
        )
        cls.registration_validated = AdmissionFactory(
            formation=cls.formation,
            state=VALIDATED,
            academic_year=cls.academic_year
        )
        group_student = GroupFactory(name=MANAGERS_GROUP)
        cls.student_worker = PersonWithPermissionsFactory(
            'can_access_admission',
            'can_edit_received_file_field',
            'can_validate_registration'
        )
        cls.student_worker.user.groups.add(group_student)

    @patch('continuing_education.views.admission.send_admission_to_queue')
    def test_registration_detail_edit_state_to_validated_as_continuing_education_manager(self, mock_queue):
        self.client.force_login(self.continuing_education_manager.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
        mock_queue.assert_called_with(self.registration_submitted)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        self.assertEqual(self.registration_submitted.state, VALIDATED, 'state')

    @patch('continuing_education.views.admission.send_admission_to_queue')
    def test_registration_detail_edit_state_to_validated_as_student_worker(self, mock_queue):
        self.client.force_login(self.student_worker.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
        mock_queue.assert_called_with(self.registration_submitted)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        self.assertEqual(self.registration_submitted.state, VALIDATED, 'state')

    @patch('continuing_education.views.admission.send_admission_to_queue')
    def test_registration_detail_edit_state_to_validated_as_faculty_manager(self, mock_queue):
        self.client.force_login(self.faculty_manager.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
        mock_queue.assert_called_with(self.registration_submitted)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        # state should not be changed and error message should be presented to user
        self.assertEqual(self.registration_submitted.state, REGISTRATION_SUBMITTED, 'state')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("Continuing education managers and student workers only are allowed to validate a registration")),
            str(messages_list[0])
        )

    def test_registration_detail_list_authorized_state_choices(self):
        for registration in [self.registration_submitted, self.registration_validated]:
            self.client.force_login(self.continuing_education_manager.user)
            url = reverse('admission_detail', args=[registration.pk])
            response = self.client.get(url)
            self.assertTemplateUsed(response, 'admission_detail.html')
            self.assertGreaterEqual(len(response.context['states']), 0)

    def test_registration_detail_empty_unauthorized_state_choices(self):
        for registration in [self.registration_submitted, self.registration_validated]:
            self.client.force_login(self.faculty_manager.user)
            url = reverse('admission_detail', args=[registration.pk])
            response = self.client.get(url)
            self.assertTemplateUsed(response, 'admission_detail.html')
            self.assertEqual(len(response.context['states']), 0)

    def _data_form_to_validate(self):
        return {
            'state': VALIDATED,
            'formation': self.formation.pk,
            'person_information': self.registration_submitted.person_information.pk,
            'academic_year': self.registration_submitted.academic_year.pk
        }


class ViewRegistrationsTrainingManagerTestCase(TestCase):
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
        group = GroupFactory(name=TRAINING_MANAGERS_GROUP)
        cls.training_manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        cls.training_manager.user.groups.add(group)

        valid_state = [REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED]
        cls.registrations = []
        for valid_state in valid_state:
            cls.registrations.append(AdmissionFactory(
                formation=cls.formation,
                state=valid_state
            ))

        for invalid_state in admission_state_choices.STATE_CHOICES:
            if invalid_state[0] not in [REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED]:
                AdmissionFactory(
                    formation=cls.formation,
                    state=invalid_state[0]
                )

    def setUp(self):
        self.client.force_login(self.training_manager.user)

    def test_list_with_no_registrations_visible(self):
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['admissions'], [])
        self.assertTemplateUsed(response, 'registrations.html')

    def test_list_with_registrations(self):
        PersonTraining(training=self.formation, person=self.training_manager).save()
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['admissions'],
                              self.registrations)
        self.assertEqual(response.context['admissions_number'], 3)
        self.assertTemplateUsed(response, 'registrations.html')


class ViewRegistrationCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        group = GroupFactory(name=MANAGERS_GROUP)
        cls.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        cls.manager.user.groups.add(group)

    def setUp(self):
        self.client.force_login(self.manager.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('registration'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('registration'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])


def _build_unauthorized_user():
    return User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')

