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
from unittest import skip
from unittest.mock import patch

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import status

from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED
from continuing_education.models.enums.ucl_registration_error_choices import UCLRegistrationError
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_student_worker import \
    ContinuingEducationStudentWorkerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class ViewRegistrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.academic_year = create_current_academic_year()
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
        self.client.force_login(self.manager.person.user)

    def test_list_registrations(self):
        url = reverse('registration')
        response = self.client.get(url)
        admissions = response.context['admissions']
        for admission in admissions:
            self.assertIn(admission.state, [admission_state_choices.ACCEPTED, admission_state_choices.VALIDATED])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'continuing_education/registrations.html')

    def test_list_registrations_pagination_empty_page(self):
        url = reverse('registration')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'continuing_education/registrations.html')

    def test_registration_edit_not_found(self):
        response = self.client.get(reverse('registration_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_edit_get_registration_found(self):
        url = reverse('registration_edit', args=[self.admission_accepted.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'continuing_education/registration_form.html')

    def test_edit_post_registration_found(self):
        new_address = AddressFactory()

        previous_ucl_registration = self.admission_accepted.previous_ucl_registration

        data = {
            'billing_address': new_address.pk,
            'billing-city': new_address.city,
            'use_address_for_billing': False,
            'residence_address': new_address.pk,
            'residence-city': new_address.city,
            'use_address_for_post': False,
            'children_number': 2,
            'previous_ucl_registration': not previous_ucl_registration,
            'ucl_registration_complete': "INSCRIT",
            'registration_file_received': True
        }

        form = RegistrationForm(data, instance=self.admission_accepted)

        url = reverse('registration_edit', args=[self.admission_accepted.id])

        response = self.client.post(url, data=data)
        self.assertRedirects(
            response,
            reverse('admission_detail', args=[self.admission_accepted.id]) + "#registration"
        )

        self.admission_accepted.refresh_from_db()

        self.assertEqual(self.admission_accepted.children_number, 2)
        self.assertEqual(self.admission_accepted.residence_address.city, new_address.city)
        self.assertEqual(self.admission_accepted.billing_address.city, new_address.city)

    def test_training_manager_should_not_update_unupdatable_fields(self):
        training_manager = ContinuingEducationTrainingManagerFactory(training=self.admission_accepted.formation)
        self.client.force_login(user=training_manager.person.user)

        registration_file_received = self.admission_accepted.registration_file_received
        data = {
            'registration_file_received': not registration_file_received,
            'ucl_registration_complete': "INSCRIT",
            'previous_ucl_registration': True,
        }
        url = reverse('registration_edit', args=[self.admission_accepted.id])

        response = self.client.post(url, data=data)
        self.assertRedirects(
            response,
            reverse('admission_detail', args=[self.admission_accepted.id]) + "#registration"
        )

        self.admission_accepted.refresh_from_db()

        self.assertEqual(self.admission_accepted.ucl_registration_complete, "INIT_STATE")
        self.assertEqual(self.admission_accepted.registration_file_received, registration_file_received)

    def test_uclouvain_registration_rejected(self):
        self.admission_validated.ucl_registration_complete = UCLRegistrationState.REJECTED.name
        self.admission_validated.ucl_registration_error = UCLRegistrationError.IUFC_NOM_TROP_LONG.name
        self.admission_validated.save()

        url = reverse('admission_detail', kwargs={'admission_id': self.admission_validated.pk})
        response = self.client.get(url)

        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        msg = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(
            gettext(_("Folder injection into EPC failed : %(reasons)s") % {
                'reasons': self.admission_validated.get_ucl_registration_error_display()
            }),
            msg
        )
        self.assertEqual(msg_level[0], messages.ERROR)

    def test_uclouvain_registration_on_demand(self):
        self.admission_validated.ucl_registration_complete = UCLRegistrationState.DEMANDE.name
        self.admission_validated.save()

        url = reverse('admission_detail', kwargs={'admission_id': self.admission_validated.pk})
        response = self.client.get(url)

        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        msg = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(gettext(_("Folder injection into EPC succeeded : UCLouvain registration on demand")), msg)
        self.assertEqual(msg_level[0], messages.INFO)

    def test_uclouvain_registration_registered(self):
        self.admission_validated.ucl_registration_complete = UCLRegistrationState.INSCRIT.name
        self.admission_validated.save()

        url = reverse('admission_detail', kwargs={'admission_id': self.admission_validated.pk})
        response = self.client.get(url)

        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        msg = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(gettext(_('Folder injection into EPC succeeded : UCLouvain registration completed')), msg)
        self.assertEqual(msg_level[0], messages.SUCCESS)

    def test_uclouvain_registration_sended(self):
        self.admission_validated.ucl_registration_complete = UCLRegistrationState.SENDED.name
        self.admission_validated.save()

        url = reverse('admission_detail', kwargs={'admission_id': self.admission_validated.pk})
        response = self.client.get(url)

        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        msg = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(gettext(_("Folder sended to EPC : waiting for response")), msg)
        self.assertEqual(msg_level[0], messages.WARNING)

    def test_uclouvain_registration_other_state(self):
        self.admission_validated.ucl_registration_complete = UCLRegistrationState.DECES.name
        self.admission_validated.save()

        url = reverse('admission_detail', kwargs={'admission_id': self.admission_validated.pk})
        response = self.client.get(url)

        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        msg = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn(gettext(_('Folder injection into EPC succeeded : UCLouvain registration status : %(status)s') % {
            'status': UCLRegistrationState.DECES.value
        }), msg)
        self.assertEqual(msg_level[0], messages.INFO)

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
        self.assertTemplateUsed(response, 'continuing_education/cancellations.html')

    def test_list_cancellations_pagination_empty_page(self):
        url = reverse('cancelled_files')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'continuing_education/cancellations.html')

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
        cls.formation = ContinuingEducationTrainingFactory(education_group=cls.education_group)
        cls.faculty_manager = ContinuingEducationTrainingManagerFactory(training=cls.formation)
        cls.continuing_education_manager = ContinuingEducationManagerFactory()
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
        cls.student_worker = ContinuingEducationStudentWorkerFactory()

    @patch('continuing_education.views.admission.send_admission_to_queue')
    def test_registration_detail_edit_state_to_validated_as_continuing_education_manager(self, mock_queue):
        self.client.force_login(self.continuing_education_manager.person.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
        mock_queue.assert_called_with(response.wsgi_request, self.registration_submitted)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        self.assertEqual(self.registration_submitted.state, VALIDATED, 'state')

    @patch('continuing_education.views.admission.send_admission_to_queue')
    def test_registration_detail_edit_state_to_validated_as_student_worker(self, mock_queue):
        self.client.force_login(self.student_worker.person.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
        mock_queue.assert_called_with(response.wsgi_request, self.registration_submitted)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        self.assertEqual(self.registration_submitted.state, VALIDATED, 'state')

    def test_registration_detail_edit_state_to_validated_as_faculty_manager(self):
        self.client.force_login(self.faculty_manager.person.user)
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=self._data_form_to_validate())
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
            self.client.force_login(self.continuing_education_manager.person.user)
            url = reverse('admission_detail', args=[registration.pk])
            response = self.client.get(url)
            self.assertTemplateUsed(response, 'continuing_education/admission_detail.html')
            self.assertGreaterEqual(len(response.context['states']), 0)

    def test_registration_detail_empty_unauthorized_state_choices(self):
        for registration in [self.registration_submitted, self.registration_validated]:
            self.client.force_login(self.faculty_manager.person.user)
            url = reverse('admission_detail', args=[registration.pk])
            response = self.client.get(url)
            self.assertTemplateUsed(response, 'continuing_education/admission_detail.html')
            self.assertEqual(len(response.context['states']), 0)

    def _data_form_to_validate(self):
        return {
            'state': VALIDATED,
            'formation': self.formation.pk,
            'person_information': self.registration_submitted.person_information.pk,
            'academic_year': self.registration_submitted.academic_year.pk,
            'email': 'test@gmail.com'
        }


class ViewRegistrationsTrainingManagerTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.training_manager = ContinuingEducationTrainingManagerFactory(training=cls.formation)

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
        self.client.force_login(self.training_manager.person.user)

    def test_list_with_no_registrations_visible(self):
        training_manager = ContinuingEducationTrainingManagerFactory()
        self.client.force_login(training_manager.person.user)
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['admissions'], [])
        self.assertTemplateUsed(response, 'continuing_education/registrations.html')

    def test_list_with_registrations(self):
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['admissions'], self.registrations)
        self.assertEqual(response.context['admissions_number'], 3)
        self.assertTemplateUsed(response, 'continuing_education/registrations.html')


class ViewRegistrationCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.academic_year = AcademicYearFactory(current=True)

    def setUp(self):
        self.client.force_login(self.manager.person.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('registration'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('registration'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])


def _build_unauthorized_user():
    return User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
