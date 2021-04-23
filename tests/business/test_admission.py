##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest.mock import patch

from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.utils.translation import gettext as _
from reversion.models import Version

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.business import admission
from continuing_education.business.admission import _get_formatted_admission_data, _get_managers_mails, \
    check_required_field_for_participant, _get_attachments, _build_participant_receivers, _participant_created_admission
from continuing_education.forms.address import ADDRESS_PARTICIPANT_REQUIRED_FIELDS
from continuing_education.forms.admission import ADMISSION_PARTICIPANT_REQUIRED_FIELDS
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import SUBMITTED
from continuing_education.models.file import AdmissionFile
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.file import AdmissionFileFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory
from continuing_education.views.common import save_and_create_revision, get_revision_messages, ADMISSION_CREATION
from osis_common.messaging import message_config
from reference.tests.factories.country import CountryFactory

CONTINUING_EDUCATION_MANAGERS_GROUP = "continuing_education_managers"


class TestAdmission(TestCase):
    def test_get_formatted_admission_data(self):
        academic_year = create_current_academic_year()
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=education_group,
            academic_year=academic_year
        )
        training = ContinuingEducationTrainingFactory(education_group=education_group)
        admission = AdmissionFactory(formation=training)
        expected_list = [
            "{} : {}".format(_('Last name'), admission.person_information.person.last_name),
            "{} : {}".format(_('First name'), admission.person_information.person.first_name),
            "{} : {}".format(_('Formation'), admission.formation.acronym),
            "{} : {}".format(_('High school diploma'), _('Yes') if admission.high_school_diploma else _('No')),
            "{} : {}".format(_('High school graduation year'), admission.high_school_graduation_year),
            "{} : {}".format(_('Last degree level'), admission.last_degree_level),
            "{} : {}".format(_('Last degree field'), admission.last_degree_field),
            "{} : {}".format(_('Last degree institution'), admission.last_degree_institution),
            "{} : {}".format(_('Last degree graduation year'), admission.last_degree_graduation_year),
            "{} : {}".format(_('Other educational background'), admission.other_educational_background),
            "{} : {}".format(_('Professional status'), admission.professional_status),
            "{} : {}".format(_('Current occupation'), admission.current_occupation),
            "{} : {}".format(_('Current employer'), admission.current_employer),
            "{} : {}".format(_('Activity sector'), admission.activity_sector),
            "{} : {}".format(_('Past professional activities'), admission.past_professional_activities),
            "{} : {}".format(_('Motivation'), admission.motivation),
            "{} : {}".format(_('Professional and personal interests'), admission.professional_personal_interests),
            "{} : {}".format(_('State'), _(admission.state)),
        ]
        self.assertListEqual(
            _get_formatted_admission_data(admission),
            expected_list
        )

    def test_get_managers_mail(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed, academic_year=create_current_academic_year())
        manager = PersonFactory(last_name="AAA")
        manager_2 = PersonFactory(last_name="BBB")
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        ContinuingEducationTrainingManagerFactory(person=manager, training=cet)
        ContinuingEducationTrainingManagerFactory(person=manager_2, training=cet)
        admission = AdmissionFactory(formation=cet)
        expected_mails = "{}{}{}".format(manager.email, _(" or "), manager_2.email)

        self.assertEqual(_get_managers_mails(admission.formation), expected_mails)

    def test_get_managers_mail_mail_missing(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed, academic_year=create_current_academic_year())
        manager = PersonFactory(last_name="AAA", email="")
        manager_2 = PersonFactory(last_name="BBB", email="")
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        ContinuingEducationTrainingManagerFactory(person=manager, training=cet)
        ContinuingEducationTrainingManagerFactory(person=manager_2, training=cet)
        admission = AdmissionFactory(formation=cet)
        expected_mails = "{}".format(manager_2.email)

        self.assertEqual(_get_managers_mails(admission.formation), expected_mails)

    @override_settings(LANGUAGES=[('fr-be', 'French'), ('en', 'English'), ], LANGUAGE_CODE='fr-be')
    def test_check_address_required_field_for_participant(self):
        an_incomplete_address = AddressFactory(
            city="",
            location="",
            postal_code=5501,
            country=None
        )

        response = check_required_field_for_participant(an_incomplete_address,
                                                        Address._meta,
                                                        ADDRESS_PARTICIPANT_REQUIRED_FIELDS)
        expected = {'country': _(Address._meta.get_field('country').verbose_name),
                    'location': _(Address._meta.get_field('location').verbose_name),
                    'city': _(Address._meta.get_field('city').verbose_name), }
        self.assertDictEqual(response, expected)

        a_complete_address = AddressFactory(city="Malonne",
                                            location="Rue du Clinchamps",
                                            postal_code=5501,
                                            country=CountryFactory())
        response = check_required_field_for_participant(a_complete_address,
                                                        Address._meta,
                                                        ADDRESS_PARTICIPANT_REQUIRED_FIELDS)
        self.assertDictEqual(response, {})

    def test_check_admission_required_field_for_participant(self):
        admission = AdmissionFactory(address=AddressFactory(),
                                     current_employer="")
        response = check_required_field_for_participant(admission,
                                                        Admission._meta,
                                                        ADMISSION_PARTICIPANT_REQUIRED_FIELDS)
        expected = {'current_employer': _(Admission._meta.get_field('current_employer').verbose_name)}
        self.assertDictEqual(response, expected)


class SendEmailTest(TestCase):
    def setUp(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed, academic_year=create_current_academic_year())
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        self.manager = ContinuingEducationTrainingManagerFactory(training=cet)
        self.other_manager = ContinuingEducationTrainingManagerFactory(
            person=PersonFactory(last_name="BBB"),
            training=cet
        )
        self.admission = AdmissionFactory(formation=cet)
        uploaded_file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode('content'),
            content_type="application/pdf"
        )

        self.admission_file = AdmissionFileFactory(
            admission=self.admission,
            path=uploaded_file,
        )

    @patch('continuing_education.business.admission.send_email')
    def test_send_state_changed_email(self, mock_send):
        self.admission.state = admission_state_choices.ACCEPTED
        self.admission._original_state = self.admission.state
        self.admission.save()
        admission.save_state_changed_and_send_email(self.admission)
        args = mock_send.call_args[1]

        self.assertEqual(_(self.admission.state), args.get('data').get('subject').get('state'))
        self.assertEqual(
            _get_managers_mails(self.admission.formation),
            args.get('data').get('template').get('mails')
        )
        self.assertEqual(
            self.admission.person_information.person.first_name,
            args.get('data').get('template').get('first_name')
        )
        self.assertEqual(
            self.admission.person_information.person.last_name,
            args.get('data').get('template').get('last_name')
        )
        self.assertEqual(
            self.admission.formation,
            args.get('data').get('template').get('formation')
        )
        self.assertEqual(
            _(self.admission.state),
            args.get('data').get('template').get('state')
        )
        self.assertEqual(
            self.admission.state_reason if self.admission.state_reason else "-",
            args.get('data').get('template').get('reason')
        )
        self.assertEqual(len(args.get('receivers')), 2)
        self.assertIsNone(args.get('attachment'))

    @patch('continuing_education.business.admission.send_email')
    def test_send_submission_email_to_admin(self, mock_send):
        admission.send_submission_email_to_admission_managers(self.admission, connected_user=None)
        args = mock_send.call_args[1]
        self.assertEqual(_(self.admission.formation.acronym), args.get('data').get('subject').get('formation'))
        self.assertEqual(
            self.admission.person_information.person.first_name,
            args.get('data').get('template').get('first_name')
        )
        self.assertEqual(
            self.admission.person_information.person.last_name,
            args.get('data').get('template').get('last_name')
        )
        self.assertEqual(
            self.admission.formation,
            args.get('data').get('template').get('formation')
        )
        self.assertEqual(
            _(self.admission.state),
            args.get('data').get('template').get('state')
        )
        relative_path = reverse('admission_detail', kwargs={'admission_id': self.admission.id})
        url = 'https://{}{}'.format(Site.objects.get_current().domain, relative_path)
        self.assertEqual(
            url,
            args.get('data').get('template').get('formation_link')
        )
        self.assertEqual(len(args.get('receivers')), 2)
        self.assertIsNone(args.get('attachment'))

    @patch('continuing_education.business.admission.send_email')
    def test_send_admission_submitted_email_to_participant(self, mock_send):
        admission.send_submission_email_to_participant(self.admission, connected_user=None)
        args = mock_send.call_args[1]

        self.assertEqual({}, args.get('data').get('subject'))
        self.assertEqual(
            _get_managers_mails(self.admission.formation),
            args.get('data').get('template').get('mails')
        )
        self.assertEqual(
            self.admission.formation.title,
            args.get('data').get('template').get('formation')
        )
        self.assertEqual(
            self.admission.person_information.person.last_name,
            args.get('data').get('template').get('name')
        )
        self.assertEqual(
            _get_formatted_admission_data(self.admission),
            args.get('data').get('template').get('admission_data')
        )
        self.assertEqual(len(args.get('receivers')), 2)
        self.assertIsNone(args.get('attachment'))

    @patch('continuing_education.business.admission.send_email')
    def test_send_invoice_uploaded_email(self, mock_send):
        admission.send_invoice_uploaded_email(self.admission)
        args = mock_send.call_args[1]

        self.assertEqual({}, args.get('data').get('subject'))
        self.assertEqual(
            _get_managers_mails(self.admission.formation),
            args.get('data').get('template').get('mails')
        )
        self.assertEqual(
            self.admission.formation.acronym,
            args.get('data').get('template').get('formation')
        )
        self.assertEqual(len(args.get('receivers')), 2)
        self.assertIsNone(args.get('attachment'))

    def test_get_attachments_with_attachment_size_nok(self):
        max_size_to_check = self.admission_file.size - 1
        self.assertIsNone(_get_attachments(self.admission.id, max_size_to_check))

    def test_get_attachments_with_attachment_size_ok(self):
        max_size_to_check = self.admission_file.size + 1
        self.assertEqual(len(_get_attachments(self.admission.id, max_size_to_check)), 1)

    def test_get_attachments_without_attachment(self):
        max_size_to_check = self.admission_file.size - 1
        AdmissionFile.objects.all().delete()
        self.assertListEqual(_get_attachments(self.admission.id, max_size_to_check), [])

    @patch('continuing_education.business.admission.send_email')
    def test_send_admission_accepted_with_condition(self, mock_send):
        self.admission.state = admission_state_choices.ACCEPTED
        self.admission._original_state = self.admission.state
        self.admission.condition_of_acceptance = 'CONDITION'
        self.admission.save()
        admission.save_state_changed_and_send_email(self.admission)
        args = mock_send.call_args[1]

        self.assertEqual(
            self.admission.condition_of_acceptance,
            args.get('data').get('template').get('condition_of_acceptance')
        )
        self.assertEqual(len(args.get('receivers')), 2)

    @patch('continuing_education.business.admission.send_email')
    def test_send_admission_with_no_registration_required(self, mock_send):
        self.admission.state = admission_state_choices.ACCEPTED
        self.admission._original_state = self.admission.state
        self.admission.formation.registration_required = False
        self.admission.condition_of_acceptance = 'CONDITION'
        self.admission.formation.save()
        self.admission.save()
        admission.save_state_changed_and_send_email(self.admission)
        args = mock_send.call_args[1]

        self.assertEqual(
            self.admission.formation.registration_required,
            args.get('data').get('template').get('registration_required')
        )
        self.assertEqual(
            self.admission.condition_of_acceptance,
            args.get('data').get('template').get('condition_of_acceptance')
        )
        self.assertEqual(len(args.get('receivers')), 2)

    def test_build_participant_receivers_2_different_emails(self):
        receivers = _build_participant_receivers(self.admission)
        excepted_receivers = [
            message_config.create_receiver(
                self.admission.person_information.person.id,
                mail,
                None
            )
            for mail in [self.admission.email, self.admission.person_information.person.email]
        ]
        self.assertCountEqual(receivers, excepted_receivers)

    def test_build_participant_receivers_1_unique_email(self):
        self.admission.email = self.admission.person_information.person.email
        self.admission.save()
        receivers = _build_participant_receivers(self.admission)
        excepted_receivers = [
            message_config.create_receiver(
                self.admission.person_information.person.id,
                self.admission.email,
                None
            )
        ]
        self.assertCountEqual(receivers, excepted_receivers)


class SendEmailSettingsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed, academic_year=create_current_academic_year())
        cls.cet = ContinuingEducationTrainingFactory(education_group=ed)
        cls.manager = ContinuingEducationTrainingManagerFactory(training=cls.cet)
        cls.admission = AdmissionFactory(formation=cls.cet)

    @patch('continuing_education.business.admission.send_email')
    def test_send_email_setting_false(self, mock_send_mail):
        self.cet.send_notification_emails = False
        self.cet.save()
        self.admission.state = SUBMITTED
        self.admission.save()

        admission.send_submission_email_to_admission_managers(self.admission, None)
        receivers = mock_send_mail.call_args[1].get('receivers')
        self.assertEqual(len(receivers), 0)

    @patch('continuing_education.business.admission.send_email')
    def test_send_email_setting_true_no_alternate_receivers(self, mock_send_mail):
        self.cet.send_notification_emails = True
        self.cet.save()
        self.admission.state = SUBMITTED
        self.admission.save()

        admission.send_submission_email_to_admission_managers(self.admission, None)
        receivers = mock_send_mail.call_args[1].get('receivers')
        self.assertEqual(
            receivers,
            [
                {
                    'receiver_person_id': self.manager.person.id,
                    'receiver_email': self.manager.person.email,
                    'receiver_lang': self.manager.person.language
                }
            ]
        )

    @patch('continuing_education.business.admission.send_email')
    def test_send_email_setting_true_with_alternate_receivers(self, mock_send_mail):
        self.cet.send_notification_emails = True
        self.cet.alternate_notification_email_addresses = "jane.doe@test.be, test2@domain.com"
        self.cet.save()
        self.admission.state = SUBMITTED
        self.admission.save()

        admission.send_submission_email_to_admission_managers(self.admission, None)
        receivers = mock_send_mail.call_args[1].get('receivers')
        self.assertCountEqual(
            receivers,
            [
                {
                    'receiver_person_id': None,
                    'receiver_email': "jane.doe@test.be",
                    'receiver_lang': message_config.DEFAULT_LANG
                },
                {
                    'receiver_person_id': None,
                    'receiver_email': "test2@domain.com",
                    'receiver_lang': message_config.DEFAULT_LANG
                }
            ]
        )

    @patch('continuing_education.business.admission.send_email')
    def test_send_email_email_missing(self, mock_send_mail):
        self.manager_without_email = ContinuingEducationTrainingManagerFactory(
            person=PersonFactory(last_name="AAA", email=""),
            training=self.cet
        )

        self.cet.send_notification_emails = True
        self.cet.save()

        admission.send_submission_email_to_admission_managers(self.admission, None)
        receivers = mock_send_mail.call_args[1].get('receivers')

        self.assertCountEqual(
            receivers,
            [
                {
                    'receiver_person_id': self.manager.person.id,
                    'receiver_email': self.manager.person.email,
                    'receiver_lang': self.manager.person.language
                },
            ]
        )

    def test_participant_created_admission_true(self):
        Version.objects.all().delete()
        self.assertFalse(_participant_created_admission(self.admission))

        save_and_create_revision(
            get_revision_messages(ADMISSION_CREATION),
            self.admission,
            self.admission.person_information.person.user
        )

        self.assertTrue(_participant_created_admission(self.admission))

    def test_participant_created_admission_false(self):
        Version.objects.all().delete()
        self.assertFalse(_participant_created_admission(self.admission))

        save_and_create_revision(
            get_revision_messages(ADMISSION_CREATION),
            self.admission,
            self.manager.person.user
        )

        self.assertFalse(_participant_created_admission(self.admission))
