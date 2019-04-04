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
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from rest_framework import status

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, WAITING, SUBMITTED
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.views.archive import _switch_archived_state, _mark_as_archived


class ViewArchiveTestCase(TestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation_1 = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation_2 = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        group = GroupFactory(name='continuing_education_managers')
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.manager.user.groups.add(group)
        self.client.force_login(self.manager.user)
        EntityVersionFactory(
            entity=self.formation_1.management_entity
        )
        self.admission_archived = AdmissionFactory(
            formation=self.formation_1,
            state=WAITING,
            archived=True
        )
        self.registration_1_unarchived = AdmissionFactory(
            formation=self.formation_2,
            state=ACCEPTED,
            archived=False
        )
        self.registration_2_archived = AdmissionFactory(
            formation=self.formation_2,
            state=ACCEPTED,
            archived=True
        )

    def test_switch_archived_state(self):
        admision_changed = _switch_archived_state(self.admission_archived.id)
        self.assertFalse(admision_changed.archived)
        admision_changed = _switch_archived_state(self.registration_1_unarchived.id)
        self.assertTrue(admision_changed.archived)

    def test_error_message_no_admission_selected(self):
        response = self.client.post(reverse('archives_procedure'),
                                    data={},
                                    follow=True,
                                    HTTP_REFERER=reverse('admission', args=[])
                                    )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _('Please select at least one file to archive'))

    def test_error_message_no_registration_selected(self):
        response = self.client.post(reverse('archives_procedure'),
                                    data={},
                                    follow=True,
                                    HTTP_REFERER=reverse('registration', args=[])
                                    )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.ERROR, msg_level)
        self.assertEqual(msg[0], _('Please select at least one file to archive'))

    def test_mark_as_archived(self):
        _mark_as_archived(self.registration_1_unarchived.id)
        ad = Admission.objects.get(id=self.registration_1_unarchived.id)
        self.assertTrue(ad.archived)

        _mark_as_archived(self.admission_archived.id)
        ad = Admission.objects.get(id=self.admission_archived.id)
        self.assertTrue(ad.archived)

    def test_mark_registration_folders_as_archived_plural(self):

        response = self.client.post(reverse('archives_procedure'),
                                    data={"selected_action": [
                                        str(self.registration_1_unarchived.id),
                                        str(self.registration_2_archived.id)
                                    ]},
                                    follow=True,
                                    HTTP_REFERER=reverse('registration', args=[])
                                    )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)

        self.assertEqual(msg[0], "{} {}".format(_('Files are now'),
                                                _('archived')))

    def test_mark_registration_folders_as_archived_single(self):

        response = self.client.post(reverse('archives_procedure'),
                                    data={"selected_action": [str(self.registration_1_unarchived.id)]},
                                    follow=True,
                                    HTTP_REFERER=reverse('registration', args=[])
                                    )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)

        self.assertEqual(msg[0], "{} {}".format(_('File is now'),
                                                _('archived')))

    def test_archive_procedure(self):
        response = self.client.post(reverse('archives_procedure'),
                                    data={"selected_action": [str(self.admission_archived.id)]},
                                    follow=True,
                                    HTTP_REFERER=reverse('admission', args=[])
                                    )
        self.assertEqual(response.status_code, 200)

        msg = [m.message for m in get_messages(response.wsgi_request)]
        msg_level = [m.level for m in get_messages(response.wsgi_request)]
        self.assertEqual(len(msg), 1)
        self.assertIn(messages.SUCCESS, msg_level)
        self.assertEqual(msg[0], "{} {}".format(_('File is now'),
                                                   _('archived')))

    def test_list(self):
        response = self.client.post(reverse('archive'))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(response.context['archives'].object_list,
                              [self.admission_archived,
                               self.registration_2_archived]
                              )

    def test_cached_filters(self):
        response = self.client.get(reverse('archive'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('archive'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])

class ViewArchiveTrainingManagerTestCase(TestCase):
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
        self.admission = AdmissionFactory(
            formation=self.formation,
            state=SUBMITTED,
        )

    def test_list_with_no_archive_visible(self):
        self.admission.archived = True
        self.admission.save()
        response = self.client.post(reverse('archive'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['archives'].object_list, [])

    def test_list_with_archive(self):
        self.admission.archived = True
        self.admission.save()
        PersonTraining(training=self.admission.formation, person=self.training_manager).save()
        response = self.client.post(reverse('archive'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['archives'].object_list, [self.admission])

    def test_archive_procedure_denied(self):
        response = self.client.post(
            reverse('archive_procedure', kwargs={'admission_id': self.admission.pk})
        )
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_archive_procedure_authorized(self):
        PersonTraining(training=self.admission.formation, person=self.training_manager).save()
        response = self.client.post(
            reverse('archive_procedure', kwargs={'admission_id': self.admission.pk})
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)
