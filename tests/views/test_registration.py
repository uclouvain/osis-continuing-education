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
from django.contrib.auth.models import User
from django.core.cache import cache
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import reverse
from django.test import TestCase
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import status

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class ViewRegistrationTestCase(TestCase):
    def setUp(self):
        group = GroupFactory(name='continuing_education_managers')
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.manager.user.groups.add(group)
        self.client.force_login(self.manager.user)
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.admission_accepted = AdmissionFactory(
            state=admission_state_choices.ACCEPTED,
            formation=self.formation
        )
        self.admission_rejected = AdmissionFactory(
            state=admission_state_choices.REJECTED,
            formation=self.formation
        )
        self.admission_validated = AdmissionFactory(
            state=admission_state_choices.VALIDATED,
            formation=self.formation
        )

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
            reverse('admission_detail', args=[self.admission_accepted.id])+ "#registration"
        )
        self.admission_accepted.refresh_from_db()

        # verifying that fields are correctly updated
        for key in form.cleaned_data.keys():
            field_value = self.admission_accepted.__getattribute__(key)
            self.assertEqual(field_value, admission_dict[key])

    def test_registration_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_detail_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission_detail', kwargs={'admission_id': self.admission_accepted.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_edit_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
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
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('cancelled_files')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RegistrationStateChangedTestCase(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.faculty_manager = PersonWithPermissionsFactory(
            'can_access_admission',
            'change_admission',
        )
        self.formation = ContinuingEducationTrainingFactory(education_group=self.education_group)
        PersonTraining(person=self.faculty_manager, training=self.formation).save()
        training_manager_group = GroupFactory(name='continuing_education_training_managers')
        self.faculty_manager.user.groups.add(training_manager_group)
        group = GroupFactory(name='continuing_education_managers')
        self.continuing_education_manager = PersonWithPermissionsFactory(
            'can_access_admission',
            'change_admission',
            'can_validate_registration'
        )
        self.continuing_education_manager.user.groups.add(group)
        EntityVersionFactory(
            entity=self.formation.management_entity
        )
        self.registration_submitted = AdmissionFactory(
            formation=self.formation,
            state=REGISTRATION_SUBMITTED
        )
        self.registration_validated = AdmissionFactory(
            formation=self.formation,
            state=VALIDATED
        )

    def test_registration_detail_edit_state_to_validated_as_continuing_education_manager(self):
        self.client.force_login(self.continuing_education_manager.user)
        registration = {
            'state': VALIDATED,
            'formation': self.formation.pk,
            'person_information': self.registration_submitted.person_information.pk
        }
        data = registration
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        self.assertEqual(self.registration_submitted.state, VALIDATED, 'state')

    def test_registration_detail_edit_state_to_validated_as_faculty_manager(self):
        self.client.force_login(self.faculty_manager.user)
        registration = {
            'state': VALIDATED,
            'formation': self.formation.pk,
            'person_information': self.registration_submitted.person_information.pk
        }
        data = registration
        url = reverse('admission_detail', args=[self.registration_submitted.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.registration_submitted.pk]))
        self.registration_submitted.refresh_from_db()
        # state should not be changed and error message should be presented to user
        self.assertEqual(self.registration_submitted.state, REGISTRATION_SUBMITTED, 'state')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("Continuing education managers only are allowed to validate a registration")),
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


class ViewRegistrationsTrainingManagerTestCase(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        group = GroupFactory(name='continuing_education_training_managers')
        self.training_manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.training_manager.user.groups.add(group)
        self.client.force_login(self.training_manager.user)

        valid_state = [REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED]
        self.registrations = []
        for valid_state in valid_state:
            self.registrations.append(AdmissionFactory(
                formation=self.formation,
                state=valid_state
            ))

        for invalid_state in admission_state_choices.STATE_CHOICES:
            if invalid_state[0] not in [REGISTRATION_SUBMITTED, VALIDATED, ACCEPTED]:
                AdmissionFactory(
                    formation=self.formation,
                    state=invalid_state[0]
                )
        # invalid_state_for_training_manager = [admission_state_choices.ACCEPTED_NO_REGISTRATION_REQUIRED,
        #                                       admission_state_choices.REJECTED,
        #                                       admission_state_choices.WAITING,
        #                                       admission_state_choices.DRAFT,
        #                                       admission_state_choices.SUBMITTED,
        #                                       admission_state_choices.CANCELLED,
        #                                       admission_state_choices.CANCELLED_NO_REGISTRATION_REQUIRED]

        # for invalid_state in invalid_state_for_training_manager:
        #     AdmissionFactory(
        #         formation=self.formation,
        #         state=invalid_state,
        #     )

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
    def setUp(self):
        group = GroupFactory(name='continuing_education_managers')
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.manager.user.groups.add(group)
        self.client.force_login(self.manager.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('registration'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('registration'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])
