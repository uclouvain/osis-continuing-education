##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonFactory
from continuing_education.business import admission
from continuing_education.business.admission import _get_formatted_admission_data, _get_managers_mails, \
    CONTINUING_EDUCATION_MANAGERS_GROUP, check_required_field_for_participant
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person_training import PersonTrainingFactory
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.forms.admission import ADMISSION_PARTICIPANT_REQUIRED_FIELDS
from continuing_education.forms.address import ADDRESS_PARTICIPANT_REQUIRED_FIELDS
from reference.tests.factories.country import CountryFactory


class TestAdmission(TestCase):
    def test_get_formatted_admission_data(self):
        academic_year = AcademicYearFactory(year=2018)
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
            "{} : {}".format(_('Professional impact'), admission.professional_impact),
            "{} : {}".format(_('State'), _(admission.state)),
        ]
        self.assertListEqual(
            _get_formatted_admission_data(admission),
            expected_list
        )

    def test_get_managers_mail(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed)
        manager = PersonFactory(last_name="AAA")
        manager_2 = PersonFactory(last_name="BBB")
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        PersonTrainingFactory(person=manager, training=cet)
        PersonTrainingFactory(person=manager_2, training=cet)
        admission = AdmissionFactory(formation=cet)
        expected_mails = "{}{}{}".format(manager.email, _(" or "), manager_2.email)

        self.assertEqual(_get_managers_mails(admission.formation), expected_mails)

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
        expected = {'city': {'verbose_name': _(Address._meta.get_field('city').verbose_name)},
                    'location': {'verbose_name': _(Address._meta.get_field('location').verbose_name)},
                    'country': {'verbose_name': _(Address._meta.get_field('country').verbose_name)}}
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
        expected = {'current_employer': {'verbose_name': _(Admission._meta.get_field('current_employer').verbose_name)}}
        self.assertDictEqual(response, expected)


class SendEmailTest(TestCase):
    def setUp(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed)
        self.manager = PersonFactory(last_name="AAA")
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        PersonTrainingFactory(person=self.manager, training=cet)
        PersonTrainingFactory(person=PersonFactory(last_name="BBB"), training=cet)
        self.admission = AdmissionFactory(formation=cet)

    @patch('continuing_education.business.admission.send_email')
    def test_send_state_changed_email(self, mock_send):
        admission.send_state_changed_email(self.admission)
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
        self.assertEqual(len(args.get('receivers')), 1)
        self.assertIsNone(args.get('attachment'))

    @patch('continuing_education.business.admission.send_email')
    def test_send_admission_submitted_email_to_admin(self, mock_send):
        group = GroupFactory(name=CONTINUING_EDUCATION_MANAGERS_GROUP)
        self.manager.user.groups.add(group)
        admission.send_admission_submitted_email_to_admin(self.admission)
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
        self.assertEqual(len(args.get('receivers')), 1)
        self.assertIsNone(args.get('attachment'))

    @patch('continuing_education.business.admission.send_email')
    def test_send_admission_submitted_email_to_participant(self, mock_send):
        admission.send_admission_submitted_email_to_participant(self.admission)
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
        self.assertEqual(
            _get_formatted_admission_data(self.admission),
            args.get('data').get('template').get('admission_data')
        )
        self.assertEqual(len(args.get('receivers')), 1)
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
        self.assertEqual(len(args.get('receivers')), 1)
        self.assertIsNone(args.get('attachment'))
