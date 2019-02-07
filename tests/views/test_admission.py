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
import datetime
import random
from unittest.mock import patch

import factory.fuzzy
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import model_to_dict
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _, ugettext
from rest_framework import status

from base.models.enums import education_group_categories
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.business.enums.rejected_reason import DONT_MEET_ADMISSION_REQUIREMENTS
from continuing_education.models.admission import Admission
from continuing_education.models.enums import file_category_choices, admission_state_choices
from continuing_education.models.enums.admission_state_choices import NEW_ADMIN_STATE, SUBMITTED, DRAFT, REJECTED, \
    ACCEPTED, VALIDATED, REGISTRATION_SUBMITTED
from continuing_education.models.file import File, MAX_ADMISSION_FILE_NAME_LENGTH
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import FileFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory

FILE_CONTENT = "test-content"


class ViewAdmissionTestCase(TestCase):
    def setUp(self):
        current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        self.formation = EducationGroupYearFactory(academic_year=self.next_acad_year)

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)
        EntityVersionFactory(
            entity=self.formation.management_entity
        )
        self.admission = AdmissionFactory(
            formation=self.formation,
            state=SUBMITTED
        )

        self.file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf"
        )

    def test_list_admissions(self):
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admissions.html')

    def test_list_admissions_pagination_empty_page(self):
        url = reverse('admission')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admissions.html')

    def test_admission_detail(self):
        url = reverse('admission_detail', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admission_detail.html')

    def test_admission_detail_not_found(self):
        response = self.client.get(reverse('admission_detail', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admission_new(self):
        url = reverse('admission_new')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_admission_new_save(self):
        admission = model_to_dict(self.admission)
        response = self.client.post(reverse('admission_new'), data=admission)
        created_admission = Admission.objects.exclude(pk=self.admission.pk).get()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertRedirects(response, reverse('admission_detail', args=[created_admission.pk]))

    def test_admission_save_with_error(self):
        admission = model_to_dict(self.admission)
        admission['person_information'] = "no valid pk"
        response = self.client.post(reverse('admission_new'), data=admission)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_admission_edit_not_found(self):
        response = self.client.get(reverse('admission_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_get_admission_found(self):
        url = reverse('admission_edit', args=[self.admission.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'admission_form.html')

    def test_edit_post_admission_found(self):
        person_information = ContinuingEducationPersonFactory()
        admission = {
            'person_information': person_information.pk,
            'motivation': 'abcd',
            'professional_impact': 'abcd',
            'formation': self.formation.pk,
            'awareness_ucl_website': True,
        }
        url = reverse('admission_edit', args=[self.admission.pk])
        response = self.client.post(url, data=admission)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]))
        self.admission.refresh_from_db()

        # verifying that fields are correctly updated
        for key in admission:
            field_value = self.admission.__getattribute__(key)
            if isinstance(field_value, datetime.date):
                field_value = field_value.strftime('%Y-%m-%d')
            if isinstance(field_value, models.Model):
                field_value = field_value.pk
            self.assertEqual(field_value, admission[key], key)

    def test_admission_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admission_detail_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('admission_detail', kwargs={'admission_id':self.admission.pk})
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
        file = FileFactory(
            admission=self.admission,
            path=uploaded_file,
            uploaded_by=self.admission.person_information.person
        )
        url = reverse('download_file', kwargs={'admission_id': self.admission.pk, 'file_id': file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UploadFileTestCase(TestCase):
    def setUp(self):
        current_acad_year = create_current_academic_year()
        next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        formation = EducationGroupYearFactory(academic_year=next_acad_year)

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)

        self.admission = AdmissionFactory(
            formation=formation,
            state=SUBMITTED
        )
        self.file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf",
        )

    def test_upload_file(self):
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': self.file,
                'file_category': file_category_choices.DOCUMENT,
            },
            format='multipart'
        )

        self.assertEqual(File.objects.get(name=self.file.name).uploaded_by, self.manager)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("The document is uploaded correctly")),
            str(messages_list[0])
        )

    @patch('continuing_education.business.admission.send_email')
    def test_upload_file_invoice_email_notification(self, mock_send_mail):
        self.admission.state = admission_state_choices.ACCEPTED
        self.admission.save()
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': self.file,
                'file_category': file_category_choices.INVOICE,
                'notify_participant': True
            },
            format='multipart'
        )
        self.assertEqual(File.objects.get(name=self.file.name).uploaded_by, self.manager)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("The document is uploaded correctly")),
            messages_list
        )
        self.assertIn(
            ugettext(_("A notification email has been sent to the participant")),
            messages_list
        )
        self.assertTrue(mock_send_mail.called)

    @patch('django.db.models.base.Model.save', side_effect=Exception)
    def test_upload_file_error(self, mock_save):
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': self.file,
                'file_category': file_category_choices.DOCUMENT,
            },
            format='multipart'
        )

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("A problem occured : the document is not uploaded")),
            str(messages_list[0])
        )

    def test_upload_file_error_name_too_long(self):
        file_name_too_long = SimpleUploadedFile(
            name='{}.pdf'.format(factory.fuzzy.FuzzyText(length=MAX_ADMISSION_FILE_NAME_LENGTH + 10).fuzz()),
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf"
        )

        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': file_name_too_long,
                'file_category': file_category_choices.DOCUMENT,
            },
            format='multipart'
        )

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            _("The name of the file is too long : maximum %(length)s characters.") % {
                'length': MAX_ADMISSION_FILE_NAME_LENGTH
            },
            str(messages_list[0])
        )

    def test_upload_file_invalid_category(self):
        self.admission.state = admission_state_choices.SUBMITTED
        self.admission.save()
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': self.file,
                'file_category': file_category_choices.INVOICE,
            },
            format='multipart'
        )

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("The status of the admission must be Accepted to upload an invoice.")),
            str(messages_list[0])
        )


class DeleteFileTestCase(TestCase):
    def setUp(self):
        current_acad_year = create_current_academic_year()
        next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        formation = EducationGroupYearFactory(academic_year=next_acad_year,)

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)

        self.admission = AdmissionFactory(
            formation=formation,
            state=SUBMITTED
        )
        self.file = FileFactory()

    def test_delete_file(self):
        self.assertEqual(File.objects.all().count(), 1)
        url = reverse('delete_file', args=[self.admission.pk, self.file.pk])
        response = self.client.get(url)

        self.assertEqual(File.objects.all().count(), 0)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("File correctly deleted")),
            str(messages_list[0])
        )

    @patch('django.db.models.query.QuerySet.delete', side_effect=Exception)
    def test_delete_file_error(self, mock_delete):
        self.assertEqual(File.objects.all().count(), 1)
        url = reverse('delete_file', args=[self.admission.pk, self.file.pk])
        response = self.client.get(url)

        self.assertEqual(File.objects.all().count(), 1)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("A problem occured during delete")),
            str(messages_list[0])
        )


class InvoiceNotificationEmailTestCase(TestCase):
    def setUp(self):
        current_acad_year = create_current_academic_year()
        next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        formation = EducationGroupYearFactory(academic_year=next_acad_year)

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)

        self.admission = AdmissionFactory(
            formation=formation,
            state=ACCEPTED
        )
        self.file = FileFactory(
            admission=self.admission
        )

        self.url = reverse('send_invoice_notification_mail', args=[self.admission.pk])

    @patch('continuing_education.business.admission.send_email')
    def test_send_mail_with_invoice(self, mock_send_mail):
        self.file.file_category = file_category_choices.INVOICE
        self.file.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("A notification email has been sent to the participant")),
            messages_list
        )
        self.assertTrue(mock_send_mail.called)

    @patch('continuing_education.business.admission.send_email')
    def test_send_mail_without_invoice(self, mock_send_mail):
        self.file.file_category = file_category_choices.DOCUMENT
        self.file.save()

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("There is no invoice for this admission, notification email not sent")),
            messages_list
        )
        self.assertNotIn(
            ugettext(_("A notification email has been sent to the participant")),
            messages_list
        )
        self.assertFalse(mock_send_mail.called)


class AdmissionStateChangedTestCase(TestCase):
    def setUp(self):
        current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        self.formation = EducationGroupYearFactory(academic_year=self.next_acad_year)
        self.manager = PersonWithPermissionsFactory(
            'can_access_admission',
            'change_admission',
            'can_validate_registration'
        )
        self.client.force_login(self.manager.user)
        EntityVersionFactory(
            entity=self.formation.management_entity
        )
        self.admission = AdmissionFactory(
            formation=self.formation,
            state=random.choice(admission_state_choices.STATE_CHOICES)[0]
        )
        self.admission_submitted = AdmissionFactory(
            formation=self.formation,
            state=SUBMITTED
        )

    @patch('continuing_education.business.admission._get_continuing_education_managers')
    @patch('osis_common.messaging.send_message.send_messages')
    def test_admission_detail_edit_state(self, mock_send, mock_managers):
        states = NEW_ADMIN_STATE[self.admission.state]['states'].copy()
        if self.admission.state == admission_state_choices.SUBMITTED:
            states.remove(DRAFT)
        if self.admission.state in states:
            states.remove(self.admission.state)
        new_state = random.choice(states)
        admission = {
            'state': new_state,
            'formation': self.formation.pk,
        }
        data = admission
        if new_state == REJECTED:
            data['rejected_reason'] = DONT_MEET_ADMISSION_REQUIREMENTS
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(url, data=data)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.pk]))
        self.admission.refresh_from_db()

        admission_state = self.admission.state
        self.assertEqual(admission_state, admission['state'], 'state')

    def test_admission_detail_edit_state_to_draft(self):
        admission_draft = {
            'formation': self.formation.pk,
            'state': DRAFT
        }
        url = reverse('admission_detail', args=[self.admission_submitted.pk])
        response = self.client.post(url, data=admission_draft)
        self.assertRedirects(response, reverse('admission'))
        self.admission_submitted.refresh_from_db()

        admission_state = self.admission_submitted.state
        self.assertEqual(admission_state, admission_draft['state'], 'state')
