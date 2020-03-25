from unittest.mock import patch

import factory.fuzzy
from django.contrib import messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext, gettext_lazy as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.models.enums import file_category_choices, admission_state_choices
from continuing_education.models.enums.admission_state_choices import SUBMITTED
from continuing_education.models.file import AdmissionFile, MAX_ADMISSION_FILE_NAME_LENGTH, ALLOWED_EXTENSIONS, \
    MAX_ADMISSION_FILES_COUNT
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.views.test_admission import FILE_CONTENT


class UploadFileTestCase(TestCase):
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

        self.manager = ContinuingEducationManagerFactory()
        self.client.force_login(self.manager.person.user)
        self.admission = AdmissionFactory(
            formation=self.formation,
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

        self.assertEqual(AdmissionFile.objects.get(name=self.admission_file.name).uploaded_by, self.manager.person)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("The document is uploaded correctly")),
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
        self.assertEqual(AdmissionFile.objects.get(name=self.admission_file.name).uploaded_by, self.manager.person)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = [str(msg) for msg in list(messages.get_messages(response.wsgi_request))]
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("The document is uploaded correctly")),
            messages_list
        )
        self.assertIn(
            gettext(_("A notification email has been sent to the participant")),
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
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("A problem occured : the document is not uploaded")),
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
        self.assertEqual(response.status_code, 302)
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
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("The status of the admission must be Accepted to upload an invoice.")),
            str(messages_list[0])
        )

    def test_upload_file_unallowed_extension(self):
        file_extension = "xyz"
        self.admission_file.name = "{}.{}".format(self.admission_file.name, file_extension)
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
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(
                _(
                    "File extension '%(extension)s' is not allowed. "
                    "Allowed extensions are: '%(allowed_extensions)s'."
                ) % {
                    "extension": file_extension,
                    "allowed_extensions": ", ".join(ALLOWED_EXTENSIONS)
                    }
                ),
            str(messages_list[0])
        )

    def test_upload_too_many_files(self):
        admission_files = [
            SimpleUploadedFile(name='file_{}.pdf'.format(i), content=b'test')
            for i in range(0, MAX_ADMISSION_FILES_COUNT+1)
        ]
        url = reverse('admission_detail', args=[self.admission.pk])
        response = {}
        for file in admission_files:
            response = self.client.post(
                url,
                data={
                    'myfile': file,
                    'file_category': file_category_choices.DOCUMENT,
                },
                format='multipart'
            )
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            _("The maximum number of files has been reached : maximum %(max)s files allowed.") % {
                'max': MAX_ADMISSION_FILES_COUNT
            }, str(messages_list[-1])
        )


class DeleteFileTestCase(TestCase):
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

        cls.manager = ContinuingEducationManagerFactory()
        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=SUBMITTED
        )
        cls.admission_file = AdmissionFileFactory(
            admission=cls.admission
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_delete_file(self):
        self.assertEqual(AdmissionFile.objects.all().count(), 1)
        url = reverse('delete_file', args=[self.admission.pk, self.admission_file.pk])
        response = self.client.get(url)

        self.assertEqual(AdmissionFile.objects.all().count(), 0)
        self.assertRedirects(response, reverse('admission_detail', args=[self.admission.id]) + '#documents')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("File correctly deleted")),
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
        self.assertEqual(response.status_code, 302)
        self.assertIn(
            gettext(_("A problem occured during delete")),
            str(messages_list[0])
        )
