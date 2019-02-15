from unittest.mock import patch

import factory.fuzzy
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.enums import file_category_choices, admission_state_choices
from continuing_education.models.enums.admission_state_choices import SUBMITTED
from continuing_education.models.file import AdmissionFile, MAX_ADMISSION_FILE_NAME_LENGTH
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.views.test_admission import FILE_CONTENT


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
        self.admission_file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode(FILE_CONTENT),
            content_type="application/pdf",
        )

    def test_upload_file(self):
        url = reverse('admission_detail', args=[self.admission.pk])
        response = self.client.post(
            url,
            data={
                'myfile': self.admission_file,
                'file_category': file_category_choices.DOCUMENT,
            },
            format='multipart'
        )

        self.assertEqual(AdmissionFile.objects.get(name=self.admission_file.name).uploaded_by, self.manager)
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
                'myfile': self.admission_file,
                'file_category': file_category_choices.INVOICE,
                'notify_participant': True
            },
            format='multipart'
        )
        self.assertEqual(AdmissionFile.objects.get(name=self.admission_file.name).uploaded_by, self.manager)
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
                'myfile': self.admission_file,
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
                'myfile': self.admission_file,
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
        self.admission_file = AdmissionFileFactory()

    def test_delete_file(self):
        self.assertEqual(AdmissionFile.objects.all().count(), 1)
        url = reverse('delete_file', args=[self.admission.pk, self.admission_file.pk])
        response = self.client.get(url)

        self.assertEqual(AdmissionFile.objects.all().count(), 0)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("File correctly deleted")),
            str(messages_list[0])
        )

    @patch('django.db.models.query.QuerySet.delete', side_effect=Exception)
    def test_delete_file_error(self, mock_delete):
        self.assertEqual(AdmissionFile.objects.all().count(), 1)
        url = reverse('delete_file', args=[self.admission.pk, self.admission_file.pk])
        response = self.client.get(url)

        self.assertEqual(AdmissionFile.objects.all().count(), 1)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEquals(response.status_code, 302)
        self.assertIn(
            ugettext(_("A problem occured during delete")),
            str(messages_list[0])
        )