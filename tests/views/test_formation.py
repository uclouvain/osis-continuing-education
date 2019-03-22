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
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from base.models.enums import education_group_types
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory

TO_ACTIVATE = "true"
TO_DEACTIVATE = "false"


class ViewFormationTestCase(TestCase):
    def setUp(self):
        continuing_education_group_type = EducationGroupTypeFactory(
            name=education_group_types.TrainingType.AGGREGATION.name,
        )

        current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        self.previous_acad_year = AcademicYearFactory(year=current_acad_year.year - 1)

        self.formation_AAAA = EducationGroupYearFactory(
            acronym="AAAA",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.formation_BBBB = EducationGroupYearFactory(
            acronym="BBBB",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.formation_ABBB = EducationGroupYearFactory(
            acronym="ABBB",
            academic_year=self.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        self.current_academic_formation = EducationGroupYearFactory(
            academic_year=current_acad_year,
            education_group_type=continuing_education_group_type
        )

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)
        self.entity_version = EntityVersionFactory(
            entity=self.formation_AAAA.management_entity,
        )

    def test_current_year_formation_list(self):
        response = self.client.get(reverse('formation'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['formations'].object_list[0], self.formation_AAAA.education_group)
        self.assertEqual(response.context['formations'].object_list[1], self.formation_ABBB.education_group)
        self.assertEqual(response.context['formations'].object_list[2], self.formation_BBBB.education_group)

    def test_formation_list(self):
        response = self.client.get(reverse('formation'),
                                   data={'acronym': 'A'})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['formations'].object_list[0], self.formation_AAAA.education_group)
        self.assertEqual(response.context['formations'].object_list[1], self.formation_ABBB.education_group)
        self.assertEqual(response.context['formations_number'], 2)


class FormationActivateTestCase(TestCase):

    def setUp(self):
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)
        self.current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=self.current_acad_year.year + 1)

        self.formation1_to_activate = ContinuingEducationTrainingFactory(active=False)
        self.formation2_to_activate = ContinuingEducationTrainingFactory(active=False)

        self.formation1_to_deactivate = ContinuingEducationTrainingFactory(active=True)
        self.formation2_to_deactivate = ContinuingEducationTrainingFactory(active=True)

        self.education_group_yr_not_organized_yet = EducationGroupYearFactory(
            academic_year=self.next_acad_year
        )

    def test_formation_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('formations_procedure')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_error_message_no_formation_selected(self):
        response = self.client.get(reverse('formations_procedure'), data={'new_state': 'false'})
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _('Please select at least one formation'))

    def test_no_new_state_selected(self):
        response = self.client.post(reverse('formations_procedure'))
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_change_existing_one_continuing_formation_to_activate(self):

        data = {
            "new_state": TO_ACTIVATE,
            "selected_action": [str(self.formation1_to_activate.education_group.id)]
        }
        msg_expected = _('Formation is now active')

        self._assert_activation_success_msg(data, msg_expected)

        self.assertTrue(ContinuingEducationTraining.objects.get(id=self.formation1_to_activate.id).active)

    def test_change_existing_several_continuing_formation_to_activate(self):

        data = {
            "new_state": TO_ACTIVATE,
            "selected_action": [
                str(self.formation1_to_activate.education_group.id),
                str(self.formation2_to_activate.education_group.id)
            ]
        }

        msg_expected = _('Formation are now active')
        self._assert_activation_success_msg(data, msg_expected)
        self.assertTrue(ContinuingEducationTraining.objects.get(id=self.formation1_to_activate.id).active)
        self.assertTrue(ContinuingEducationTraining.objects.get(id=self.formation2_to_activate.id).active)

    def test_change_existing_one_continuing_formation_to_deactivate(self):

        data = {
            "new_state": TO_DEACTIVATE,
            "selected_action": [str(self.formation1_to_deactivate.education_group.id)]
        }
        msg_expected = _('Formation is now inactive')

        self._assert_activation_success_msg(data, msg_expected)

        self.assertFalse(ContinuingEducationTraining.objects.get(id=self.formation1_to_deactivate.id).active)

    def test_change_existing_several_continuing_formation_to_deactivate(self):

        data = {
            "new_state": TO_DEACTIVATE,
            "selected_action": [
                str(self.formation1_to_deactivate.education_group.id),
                str(self.formation2_to_deactivate.education_group.id)
            ]
        }

        msg_expected = _('Formation are now inactive')
        self._assert_activation_success_msg(data, msg_expected)
        self.assertFalse(ContinuingEducationTraining.objects.get(id=self.formation1_to_deactivate.id).active)
        self.assertFalse(ContinuingEducationTraining.objects.get(id=self.formation2_to_deactivate.id).active)

    def test_activate_education_group_year_not_organized_yet(self):

        data = {
            "new_state": TO_ACTIVATE,
            "selected_action": [str(self.education_group_yr_not_organized_yet.education_group.id)]
        }
        msg_expected = _('Formation is now active')

        self._assert_activation_success_msg(data, msg_expected)
        new_continuing_education_training = ContinuingEducationTraining.objects.get(
            education_group=self.education_group_yr_not_organized_yet.education_group.id
        )
        self.assertTrue(new_continuing_education_training.active)

    def _assert_activation_success_msg(self, data_dict, msg_expected):
        response = self.client.get(reverse('formations_procedure'), data=data_dict)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)
        self.assertEqual(msg[0], msg_expected)
