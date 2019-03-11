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
import random
from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext as _

from base.tests.factories.education_group import EducationGroupFactory
from continuing_education.models import admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.models.enums.entity_type import SCHOOL, FACULTY
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory


class TestAdmission(TestCase):
    def setUp(self):
        self.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.admission = AdmissionFactory(formation=self.formation)
        self.submitted_admission = AdmissionFactory(state=admission_state_choices.SUBMITTED, formation=self.formation)
        self.person = ContinuingEducationPersonFactory()

    def test_search(self):
        an_admission = self.admission
        persisted_admission = admission.search(person=an_admission.person_information)
        self.assertTrue(persisted_admission.exists())

        nonexistent_admission = admission.search(person=self.person)
        self.assertFalse(nonexistent_admission.exists())

    @patch('osis_common.messaging.send_message.send_messages')
    def test_mail_sent_on_admission_state_changed(self, mock):
        state_values = [x[0] for x in admission_state_choices.STATES_REJECTED_WAITING['choices']]
        # When state is draft, no mail are sent : mock not called
        state = random.choice(state_values)
        self.submitted_admission.state = state
        self.submitted_admission.save()
        self.assertTrue(mock.called)
        message_content = mock.call_args[0][0]
        self.assertIn(_(self.submitted_admission.state), str(message_content['template_base_data']))
        self.assertIn(self.submitted_admission.person_information.person.user.email, str(message_content['receivers']))

    @patch('osis_common.messaging.send_message.send_messages')
    def test_mail_not_sent_on_same_admission_state(self, mock):
        self.submitted_admission.save()
        self.assertFalse(mock.called)

    @patch('continuing_education.business.admission._get_continuing_education_managers')
    @patch('osis_common.messaging.send_message.send_messages')
    def test_mails_sent_to_admin_and_participant_on_admission_submitted(self, mock_send, mock_managers):
        self.admission.state = admission_state_choices.DRAFT
        self.admission.save()
        self.admission.state = admission_state_choices.SUBMITTED
        self.admission.save()
        self.assertTrue(mock_send.called)
        self.assertTrue(mock_managers.called)
        message_content = mock_send.call_args[0][0]
        self.assertIn(_(self.admission.state), str(message_content['template_base_data']))
        receivers = mock_send.call_args[0][0]['receivers']
        self.assertIn(self.admission.person_information.person.user.email, str(receivers))


class TestAdmissionGetFaculty(TestCase):

    def setUp(self):
        entities = create_entities_hierarchy()
        self.faculty = entities['child_one_entity_version']
        self.child_entity = EntityFactory(country=entities['country'], organization=entities['organization'])
        self.child_entity_version = EntityVersionFactory(acronym="CHILD_1_UNDER_FAC",
                                                         parent=self.faculty.entity,
                                                         entity_type=SCHOOL,
                                                         end_date=None,
                                                         entity=self.child_entity,
                                                         start_date=entities['start_date'])
        self.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(
            education_group=self.education_group,
            management_entity=self.child_entity
        )
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )

    def test_get_faculty(self):
        an_admission = AdmissionFactory(
            formation=self.formation
        )
        self.assertEqual(an_admission.get_faculty(), self.child_entity)
