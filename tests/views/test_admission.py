##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
import random
from unittest import mock
from unittest.mock import patch

from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.forms import model_to_dict
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import status

from base.models.person import Person
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.business.enums.rejected_reason import DONT_MEET_ADMISSION_REQUIREMENTS
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums import file_category_choices, admission_state_choices
from continuing_education.models.enums.admission_state_choices import (
    NEW_ADMIN_STATE, SUBMITTED, DRAFT, REJECTED,
    ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED,
)
from continuing_education.models.enums.groups import STUDENT_WORKERS_GROUP
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory
from continuing_education.views.admission import admission_detail
from continuing_education.views.common import (
    get_versions, save_and_create_revision, VERSION_MESSAGES,
    get_revision_messages,
)
from reference.tests.factories.country import CountryFactory

FILE_CONTENT = "test-content"


class ViewAdmissionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group,
            additional_information_label='additional_information',
            registration_required=True
        )
        cls.education_group_no_registration_required = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group_no_registration_required,
            academic_year=cls.academic_year
        )
        cls.formation_no_registration_required = ContinuingEducationTrainingFactory(
            education_group=cls.education_group_no_registration_required,
            registration_required=False
        )
        cls.manager = ContinuingEducationManagerFactory()
        cls.training_manager = ContinuingEducationTrainingManagerFactory(training=cls.formation)
        EntityVersionFactory(
            entity=cls.formation.management_entity
        )
        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=SUBMITTED,
            person_information__person__gender='H',
            academic_year=cls.academic_year,
        )
        a_person_information = ContinuingEducationPersonFactory(person__gender='H')
        cls.admission_no_admission_required = AdmissionFactory(
            formation=cls.formation_no_registration_required,
            state=ACCEPTED_NO_REGISTRATION_REQUIRED,
            person_information=a_person_information,
            academic_year=cls.academic_year,
        )

        cls.file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf"
        )
        cls.country = CountryFactory()
        cls.person_data = {
            'last_name': cls.admission.person_information.person.last_name,
            'first_name': cls.admission.person_information.person.first_name,
            'gender': cls.admission.person_information.person.gender,
            'email': cls.admission.person_information.person.email,
        }
        cls.continuing_education_person_data = {
            'birth_date': cls.admission.person_information.birth_date.strftime('%Y-%m-%d'),
            'birth_location': cls.admission.person_information.birth_location,
            'birth_country': cls.admission.person_information.birth_country.id,
        }

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_list_admissions(self):
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admissions.html')
        self.assertEqual(len(response.context['admissions'].object_list), 2)

    def test_list_admissions_filtered_by_training_manager_with_no_admission(self):
        other_training_manager = ContinuingEducationTrainingManagerFactory()
        self.client.force_login(other_training_manager.person.user)
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context['admissions'].object_list), 0)
        self.assertTemplateUsed(response, 'continuing_education/admissions.html')

    def test_list_admissions_filtered_by_training_manager_with_admission(self):
        training_manager = ContinuingEducationTrainingManagerFactory(training=self.formation)
        self.client.force_login(training_manager.person.user)
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.context['admissions'].object_list), 1)
        self.assertTemplateUsed(response, 'continuing_education/admissions.html')

    def test_list_admissions_pagination_empty_page(self):
        url = reverse('admission')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admissions.html')

    def test_admission_detail(self):
        url = reverse('admission_detail', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_detail.html')

    def test_admission_detail_not_found(self):
        response = self.client.get(reverse('admission_detail', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admission_detail_access_denied(self):
        other_training_manager = ContinuingEducationTrainingManagerFactory()
        self.client.force_login(other_training_manager.person.user)
        url = reverse('admission_detail', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_admission_new(self):
        url = reverse('admission_new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_form.html')

    def test_admission_new_save(self):
        admission = model_to_dict(self.admission)
        admission.update(self.person_data)
        admission.update(self.continuing_education_person_data)
        admissions = Admission.objects.all()
        qs_to_find_new_admissions = Admission.objects.all()
        for a in admissions:
            qs_to_find_new_admissions = qs_to_find_new_admissions.exclude(pk=a.id)
        response = self.client.post(reverse('admission_new'), data=admission)
        created_admission = qs_to_find_new_admissions.first()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('admission_detail', args=[created_admission.pk]))

    def test_admission_new_save_email(self):
        admission = model_to_dict(self.admission)
        admission.update(self.person_data)
        admission.update(self.continuing_education_person_data)
        admission.pop("person_information")
        new_admission_email = 'toto@uclouvain.be'
        admission['email'] = new_admission_email
        admissions = Admission.objects.all()
        qs_to_find_new_admissions = Admission.objects.all()
        for a in admissions:
            qs_to_find_new_admissions = qs_to_find_new_admissions.exclude(pk=a.id)
        self.client.post(reverse('admission_new'), data=admission)
        created_admission = qs_to_find_new_admissions.first()
        self.assertEqual(created_admission.person_information.person.email, new_admission_email)

    def test_admission_new_save_gender_required_if_new_person(self):
        admission = model_to_dict(self.admission)
        admission.update(self.person_data)
        admission.update(self.continuing_education_person_data)
        admission.pop("person_information")
        admission['gender'] = ""
        response = self.client.post(reverse('admission_new'), data=admission)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_form.html')

    def test_admission_new_save_gender_not_required_if_existing_person(self):
        admission = model_to_dict(self.admission)
        admission.update(self.person_data)
        admission.update(self.continuing_education_person_data)
        admission['gender'] = ""
        admissions = Admission.objects.all()
        qs_to_find_new_admissions = Admission.objects.all()
        for a in admissions:
            qs_to_find_new_admissions = qs_to_find_new_admissions.exclude(pk=a.id)
        response = self.client.post(reverse('admission_new'), data=admission)
        created_admission = qs_to_find_new_admissions.first()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('admission_detail', args=[created_admission.pk]))

    def test_admission_save_with_error(self):
        admission = model_to_dict(self.admission)
        admission['person_information'] = "no valid pk"
        response = self.client.post(reverse('admission_new'), data=admission)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_form.html')

    def test_admission_edit_not_found(self):
        response = self.client.get(reverse('admission_edit', kwargs={
            'admission_id': 1,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_get_admission_found(self):
        url = reverse('admission_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_form.html')

    def test_edit_post_admission_found(self):
        admission = {
            'person_information': self.admission.person_information.pk,
            'motivation': 'abcd',
            'professional_personal_interests': 'abcd',
            'formation': self.formation.pk,
            'awareness_ucl_website': True,
            'academic_year': self.admission.academic_year.id,
        }
        data = admission.copy()
        # Data to update
        data_person_updated = self.person_data.copy()
        data_person_updated.update({'gender': 'F'})
        data.update(data_person_updated.copy())
        # Data to update
        data_person_information_updated = self.continuing_education_person_data
        data_person_information_updated.update({'birth_location': 'namur'})
        data.update(data_person_information_updated.copy())

        new_email = 'new_email@uclouvain.be'
        data.update({'email': new_email})

        person_objects_quantity = Person.objects.all().count()
        continuing_education_person_objects_quantity = ContinuingEducationPerson.objects.all().count()

        url = reverse('admission_edit', args=[self.admission.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]))
        self.admission.refresh_from_db()
        self.admission.person_information.refresh_from_db()
        self.admission.person_information.person.refresh_from_db()

        # verifying that fields are correctly updated
        self._check_update_correct(admission, self.admission)
        self._check_update_correct(data_person_updated, self.admission.person_information.person)
        self._check_update_correct(self.continuing_education_person_data, self.admission.person_information)

        # Email must be updated in admission object but not in existing person object
        self.assertEqual(self.admission.email, new_email)
        self.assertNotEqual(self.admission.person_information.person.email, new_email)

        # Assert that we did not create new person and continuing_education_person
        self.assertEqual(person_objects_quantity, Person.objects.all().count())
        self.assertEqual(continuing_education_person_objects_quantity, ContinuingEducationPerson.objects.all().count())

    def _check_update_correct(self, data, db_obj):
        for key in data:
            field_value = db_obj.__getattribute__(key)
            if isinstance(field_value, datetime.date):
                field_value = field_value.strftime('%Y-%m-%d')
            if isinstance(field_value, models.Model):
                field_value = field_value.pk
            self.assertEqual(field_value, data[key], key)

    def test_admission_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admission_detail_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission_detail', kwargs={'admission_id': self.admission.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admission_edit_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission_edit', kwargs={'admission_id': self.admission.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admission_download_file(self):
        uploaded_file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode('content'),
            content_type="application/pdf"
        )
        admission_file = AdmissionFileFactory(
            admission=self.admission,
            path=uploaded_file,
            uploaded_by=self.admission.person_information.person
        )
        url = reverse('download_file', kwargs={'admission_id': self.admission.pk, 'file_id': admission_file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list(self):
        response = self.client.post(reverse('admission'))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['admissions'].object_list,
                              [self.admission, self.admission_no_admission_required])

    def test_get_versions(self):
        version_list = get_versions(self.admission)

        self.assertEqual(len(version_list), 0)
        i = 1
        for msg in VERSION_MESSAGES:
            save_and_create_revision(
                get_revision_messages({'icon': '', 'text': msg}),
                self.admission,
                self.training_manager.person.user
            )
            version_list = get_versions(self.admission)
            self.assertEqual(len(version_list), i)
            i += 1

    def test_ajax_get_formation_information(self):
        response = self.client.get(reverse('get_formation_information'), data={
            'formation_id': self.formation.pk
        }, headers={"x-requested-with": 'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf-8')),
                         {'additional_information_label': 'additional_information'}
                         )

    def test_error_message_no_draft_admission_selected(self):
        response = self.client.post(
            reverse('admission_delete_draft'),
            data={},
            follow=True,
            headers={"referer": reverse('admission', args=[])}
        )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _("Please select at least one admission in 'draft' status"))

    def test_draft_deleted(self):
        draf_admission = AdmissionFactory(
            state=DRAFT,
            archived=False
        )
        self.assertTrue(Admission.objects.filter(id=draf_admission.id).exists())
        response = self.client.post(
            reverse('admission_delete_draft'),
            data={'selected_draft_action': draf_admission.id},
        )
        self.assertFalse(Admission.objects.filter(id=draf_admission.id).exists())


class InvoiceNotificationEmailTestCase(TestCase):
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

        cls.manager = ContinuingEducationManagerFactory()

        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=ACCEPTED
        )
        cls.admission_file = AdmissionFileFactory(
            admission=cls.admission
        )

        cls.url = reverse('send_invoice_notification_mail', args=[cls.admission.pk])

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    @patch('continuing_education.business.admission.send_email')
    def test_send_mail_with_invoice(self, mock_send_mail):
        self.admission_file.file_category = file_category_choices.INVOICE
        self.admission_file.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("A notification email has been sent to the participant")),
            messages_list
        )
        self.assertTrue(mock_send_mail.called)

    @patch('continuing_education.business.admission.send_email')
    def test_send_mail_without_invoice(self, mock_send_mail):
        self.admission_file.file_category = file_category_choices.DOCUMENT
        self.admission_file.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("There is no invoice for this admission, notification email not sent")),
            messages_list
        )
        self.assertNotIn(
            gettext(_("A notification email has been sent to the participant")),
            messages_list
        )
        self.assertFalse(mock_send_mail.called)


class AdmissionStateChangedTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.manager = ContinuingEducationManagerFactory()
        EntityVersionFactory(
            entity=education_group_year.management_entity
        )
        cls.admission = AdmissionFactory(
            academic_year=cls.academic_year,
            formation=cls.formation,
            state=random.choice(admission_state_choices.STATE_CHOICES)[0]
        )
        cls.admission_submitted = AdmissionFactory(
            academic_year=cls.academic_year,
            formation=cls.formation,
            state=SUBMITTED
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    @patch('continuing_education.views.admission.send_admission_to_queue')
    @patch('continuing_education.business.admission._get_continuing_education_managers')
    @patch('osis_common.messaging.send_message.send_messages')
    def test_admission_detail_edit_state(self, mock_send, mock_managers, mock_queue):
        states = NEW_ADMIN_STATE[self.admission.state]['states'].copy()
        if self.admission.state == admission_state_choices.SUBMITTED:
            states.remove(DRAFT)
        if self.admission.state in states:
            states.remove(self.admission.state)
        new_state = random.choice(states)
        admission = {
            'state': new_state,
            'formation': self.formation.pk,
            'person_information': self.admission.person_information.pk,
            'email': 'test@gmail.com'
        }
        data = admission
        if new_state == REJECTED:
            data['rejected_reason'] = DONT_MEET_ADMISSION_REQUIREMENTS
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse(admission_detail, args=[self.admission.pk]))
        self.admission.refresh_from_db()
        self.assertEqual(self.admission.state, admission['state'], 'state')
        if self.admission.state == admission_state_choices.VALIDATED:
            self.assertTrue(mock_queue.called)

    @mock.patch('continuing_education.business.admission.send_email')
    def test_admission_detail_edit_state_to_draft(self, mock_send_email):
        admission_draft = {
            'formation': self.formation.pk,
            'state': DRAFT,
            'person_information': self.admission.person_information.pk,
            'email': 'test@gmail.com'
        }
        url = reverse('admission_detail', args=[self.admission_submitted.pk])
        response = self.client.post(url, data=admission_draft)
        self.assertRedirects(response, url)
        self.admission_submitted.refresh_from_db()
        self.assertEqual(self.admission_submitted.state, DRAFT, 'state')

        self.assertTrue(mock_send_email.called)
        mock_call_args = mock_send_email.call_args[1]
        self.assertEqual(
            mock_call_args.get('template_references').get('html'),
            'iufc_participant_state_changed_other_html'
        )
        receivers = mock_call_args.get('receivers')
        self.assertCountEqual(
            [receiver.get('receiver_email') for receiver in receivers],
            [self.admission_submitted.email, self.admission_submitted.person_information.person.email]
        )


class ViewAdmissionCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):

        cls.manager = ContinuingEducationManagerFactory()
        cls.academic_year = AcademicYearFactory(current=True)

    def setUp(self):
        self.client.force_login(self.manager.person.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('admission'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('admission'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])


class BillingEditTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group,
            registration_required=False
        )
        cls.manager = ContinuingEducationManagerFactory()
        cls.student_worker = PersonWithPermissionsFactory('view_admission', groups=[STUDENT_WORKERS_GROUP])
        EntityVersionFactory(
            entity=cls.formation.management_entity
        )
        a_person_information = ContinuingEducationPersonFactory(person__gender='H')
        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=SUBMITTED,
            person_information=a_person_information,
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_billing_edit(self):
        url = reverse('billing_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'continuing_education/admission_billing_form.html')

    def test_billing_edit_not_found(self):
        response = self.client.get(reverse('billing_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_billing_edit_access_denied_for_student_worker(self):
        self.client.force_login(self.student_worker.user)
        url = reverse('billing_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_billing_edit_access_denied_if_draft(self):
        self.admission.state = DRAFT
        self.admission.save()
        url = reverse('billing_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_billing_edit_access_denied_if_registration_required(self):
        self.admission.formation.registration_required = True
        self.admission.formation.save()
        url = reverse('billing_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_billing_edit_post_admission_found(self):
        billing_info = {
            'billing_address': self.admission.address.pk,
            'registration_type': 'PRIVATE',
            'head_office_name': 'HEAD_OFF_NAME',
            'company_number': 'COMP_NUM',
            'vat_number': 'VAT_NUM',
            'use_address_for_billing': True
        }
        data = billing_info.copy()

        url = reverse('billing_edit', args=[self.admission.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#billing')
        self.admission.refresh_from_db()
        self.assertEqual(self.admission.registration_type, billing_info['registration_type'])
        self.assertEqual(self.admission.head_office_name, billing_info['head_office_name'])
        self.assertEqual(self.admission.company_number, billing_info['company_number'])
        self.assertEqual(self.admission.vat_number, billing_info['vat_number'])
        self.assertEqual(self.admission.use_address_for_billing, billing_info['use_address_for_billing'])
