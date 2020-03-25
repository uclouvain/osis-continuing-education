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

from django import http
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.forms import model_to_dict
from django.http.response import HttpResponseBase
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import status

from base.models.enums import education_group_types
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.formation import ContinuingEducationTrainingForm
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person_training import PersonTrainingFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.views.formation import _set_error_message

STR_TRUE = "True"
STR_FALSE = "False"
STR_NONE = "None"


class ViewFormationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        continuing_education_group_type = EducationGroupTypeFactory(
            name=education_group_types.TrainingType.AGGREGATION.name,
        )

        current_acad_year = create_current_academic_year()
        cls.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        cls.previous_acad_year = AcademicYearFactory(year=current_acad_year.year - 1)

        cls.formation_AAAA = EducationGroupYearFactory(
            acronym="AAAA",
            partial_acronym="AAAA",
            academic_year=cls.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        cls.formation_BBBB = EducationGroupYearFactory(
            acronym="BBBB",
            partial_acronym="BBBB",
            academic_year=cls.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        cls.formation_ABBB = EducationGroupYearFactory(
            acronym="ABBB",
            partial_acronym="ABBB",
            academic_year=cls.next_acad_year,
            education_group_type=continuing_education_group_type
        )
        cls.current_academic_formation = EducationGroupYearFactory(
            acronym="DDDD",
            partial_acronym="DDDD",
            academic_year=current_acad_year,
            education_group_type=continuing_education_group_type
        )
        cls.manager = ContinuingEducationManagerFactory()
        group = GroupFactory(name='continuing_education_training_managers')
        cls.training_manager = PersonWithPermissionsFactory(
            'view_admission', 'change_admission',
            'view_continuingeducationtraining', 'change_continuingeducationtraining'
        )
        cls.training_manager.user.groups.add(group)
        cls.entity_version = EntityVersionFactory(
            entity=cls.formation_AAAA.management_entity,
        )
        cls.continuing_education_training = ContinuingEducationTrainingFactory(
            education_group=cls.formation_AAAA.education_group
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

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

    def test_formation_detail(self):
        url = reverse('formation_detail', args=[self.continuing_education_training.education_group.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'formation_detail.html')

    def test_formation_detail_not_found(self):
        response = self.client.get(reverse('formation_detail', kwargs={
            'formation_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTemplateUsed(response, 'page_not_found.html')

    def test_formation_edit_not_found(self):
        response = self.client.get(reverse('formation_edit', kwargs={
            'formation_id': 0,
        }))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_get_formation_found(self):
        url = reverse('formation_edit', args=[self.continuing_education_training.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'formation_form.html')

    def test_formation_edit_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('formation_edit', kwargs={'formation_id': self.continuing_education_training.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_post_formation_found(self):
        address = AddressFactory()
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed)
        cet = ContinuingEducationTrainingFactory(postal_address=None, education_group=ed)
        cet_dict = model_to_dict(cet)
        cet_dict['training_aid'] = not cet.training_aid
        cet_dict['active'] = not cet.active
        cet_dict['postal_address'] = model_to_dict(address)

        form = ContinuingEducationTrainingForm(cet_dict)
        form.is_valid()
        url = reverse('formation_edit', args=[cet.pk])
        response = self.client.post(url, data=form.cleaned_data)

        self.assertRedirects(response, reverse('formation_detail', args=[cet.education_group.id]))
        cet.refresh_from_db()

        # verifying that fields are correctly updated
        for key in form.cleaned_data.keys():
            field_value = cet.__getattribute__(key)
            self.assertEqual(field_value, cet_dict[key])

    def test_training_manager_can_edit_training(self):
        self.client.force_login(self.training_manager.user)
        PersonTrainingFactory(person=self.training_manager, training=self.continuing_education_training)
        url = reverse('formation_edit', args=[self.continuing_education_training.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseBase.status_code)
        self.assertTemplateUsed(response, 'formation_form.html')

    def test_training_manager_cannot_edit_training(self):
        self.client.force_login(self.training_manager.user)
        url = reverse('formation_edit', args=[self.continuing_education_training.id])
        response = self.client.get(url)
        self.assertRedirects(
            response,
            reverse('formation_detail', args=[self.continuing_education_training.education_group.id])
        )
        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _('You are not authorized to edit this training'))

    def test_context_manager_contents(self):
        self.client.force_login(self.manager.person.user)
        response = self.client.get(reverse('formation'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['continuing_education_training_manager'])
        self.assertIsNone(response.context['trainings_managing'])

    def test_context_trainer_manager_contents(self):
        training_manager_person_training = PersonTrainingFactory(person=self.training_manager,
                                                                 training=self.continuing_education_training)
        self.client.force_login(self.training_manager.user)
        response = self.client.get(reverse('formation'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['continuing_education_training_manager'])
        self.assertCountEqual(response.context['trainings_managing'], [training_manager_person_training.training.id])

    def test_set_error_message_no_formation_inactivated(self):
        input_values = [None, 'New state']
        messages_expected = [_('No formation inactivated'),  _('No formation activated')]

        url = reverse('formation')
        for idx, input_value in enumerate(input_values):
            response = self.client.post(url)
            self.assertEqual(response.status_code, 200)
            _set_error_message(input_value, response.wsgi_request)

            messages_build = get_messages(response.wsgi_request)
            self.assertEqual(len(messages_build), 1)

            for m in messages_build:
                self.assertEqual(str(m), messages_expected[idx])
                self.assertEqual(m.level, 40)


class FormationActivateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.current_acad_year = create_current_academic_year()
        cls.next_acad_year = AcademicYearFactory(year=cls.current_acad_year.year + 1)

        cls.formation1_to_activate = ContinuingEducationTrainingFactory(active=False)
        cls.formation2_to_activate = ContinuingEducationTrainingFactory(active=False)

        cls.formation1_to_deactivate = ContinuingEducationTrainingFactory(active=True)
        cls.formation2_to_deactivate = ContinuingEducationTrainingFactory(active=True)

        cls.education_group_yr_not_organized_yet = EducationGroupYearFactory(
            academic_year=cls.next_acad_year
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_formation_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('update_formations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, http.HttpResponseForbidden.status_code)

    def test_error_message_no_formation_selected(self):
        response = self.client.get(reverse('update_formations'), data={'new_state': 'false'})
        self.assertEqual(response.status_code, http.HttpResponseRedirect.status_code)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _('Please select at least one formation'))

    def test_no_new_state_selected(self):
        response = self.client.post(reverse('update_formations'))
        self.assertEqual(response.status_code, http.HttpResponseRedirect.status_code)

    def test_change_existing_one_continuing_formation_to_activate(self):

        data = {
            "new_state": STR_TRUE,
            "new_training_aid_value": STR_NONE,
            "selected_action": [str(self.formation1_to_activate.education_group.id)]
        }
        msg_expected = _('Formation is now active')

        self._assert_activation_success_msg(data, msg_expected)

        self.assertTrue(ContinuingEducationTraining.objects.get(id=self.formation1_to_activate.id).active)

    def test_change_existing_several_continuing_formation_to_activate(self):

        data = {
            "new_state": STR_TRUE,
            "new_training_aid_value": STR_NONE,
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
            "new_state": STR_FALSE,
            "new_training_aid_value": STR_NONE,
            "selected_action": [str(self.formation1_to_deactivate.education_group.id)]
        }
        msg_expected = _('Formation is now inactive')

        self._assert_activation_success_msg(data, msg_expected)

        self.assertFalse(ContinuingEducationTraining.objects.get(id=self.formation1_to_deactivate.id).active)

    def test_change_existing_several_continuing_formation_to_deactivate(self):

        data = {
            "new_state": STR_FALSE,
            "new_training_aid_value": STR_NONE,
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
            "new_state": STR_TRUE,
            "new_training_aid_value": STR_NONE,
            "selected_action": [str(self.education_group_yr_not_organized_yet.education_group.id)]
        }
        msg_expected = _('Formation is now active')

        self._assert_activation_success_msg(data, msg_expected)
        new_continuing_education_training = ContinuingEducationTraining.objects.get(
            education_group=self.education_group_yr_not_organized_yet.education_group.id
        )
        self.assertTrue(new_continuing_education_training.active)

    def _assert_activation_success_msg(self, data_dict, msg_expected):
        response = self.client.get(reverse('update_formations'), data=data_dict)
        self.assertEqual(response.status_code, http.HttpResponseRedirect.status_code)
        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)
        self.assertEqual(msg[0], msg_expected)


class FormationAidTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()
        cls.education_group_1 = EducationGroupFactory()
        cls.continuing_education_training_1 = ContinuingEducationTrainingFactory(
            education_group=cls.education_group_1,
            training_aid=False
        )
        cls.education_group_2 = EducationGroupFactory()

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_set_training_aid(self):
        data = {
            "new_training_aid_value": STR_TRUE,
            "new_state": STR_NONE,
            "selected_action": [
                str(self.education_group_1.id),
                str(self.education_group_2.id),
            ]
        }
        response = self.client.get(reverse('update_formations'), data=data)

        self.continuing_education_training_1.refresh_from_db()
        self.assertTrue(self.continuing_education_training_1.training_aid)

        continuing_education_training_2 = ContinuingEducationTraining.objects.get(
            education_group=self.education_group_2
        )
        self.assertTrue(continuing_education_training_2.training_aid)

        self.assertEqual(response.status_code, http.HttpResponseRedirect.status_code)
        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)
        msg_expected = _('Successfully defined training aid to %(new_value)s for %(quantity_updated)s trainings.') % {
            "new_value": _('Yes'),
            "quantity_updated": 2,
        }
        self.assertEqual(msg[0], msg_expected)


class ViewFormationCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()

    def setUp(self):
        self.client.force_login(self.manager.person.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('formation'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('formation'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])
