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

from django.contrib import messages
from django.contrib.messages import get_messages
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, WAITING, SUBMITTED, \
    ACCEPTED_NO_REGISTRATION_REQUIRED
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory
from continuing_education.views.archive import _switch_archived_state, _mark_as_archived


class ViewArchiveTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation_1 = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation_2 = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )

        cls.manager = ContinuingEducationManagerFactory()
        EntityVersionFactory(
            entity=cls.formation_1.management_entity
        )
        cls.admission_archived = AdmissionFactory(
            formation=cls.formation_1,
            state=WAITING,
            archived=True
        )
        cls.admission_no_registration_required_archived = AdmissionFactory(
            formation=cls.formation_1,
            state=ACCEPTED_NO_REGISTRATION_REQUIRED,
            archived=True
        )
        cls.registration_1_unarchived = AdmissionFactory(
            formation=cls.formation_2,
            state=ACCEPTED,
            archived=False
        )
        cls.registration_2_archived = AdmissionFactory(
            formation=cls.formation_2,
            state=ACCEPTED,
            archived=True
        )

    def setUp(self):
        self.client.force_login(self.manager.person.user)

    def test_switch_archived_state(self):
        admision_changed = _switch_archived_state(self.manager.person.user, self.admission_archived.id)
        self.assertFalse(admision_changed.archived)
        admision_changed = _switch_archived_state(self.manager.person.user, self.registration_1_unarchived.id)
        self.assertTrue(admision_changed.archived)

    def test_error_message_no_admission_selected(self):
        response = self.client.post(
            reverse('archives_procedure'),
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
        _mark_as_archived(self.manager.person.user, self.registration_1_unarchived.id)
        ad = Admission.objects.get(id=self.registration_1_unarchived.id)
        self.assertTrue(ad.archived)

        _mark_as_archived(self.manager.person.user, self.admission_archived.id)
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
                               self.registration_2_archived,
                               self.admission_no_registration_required_archived]
                              )


class ViewArchiveTrainingManagerTestCase(TestCase):
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
        cls.training_manager = ContinuingEducationTrainingManagerFactory()
        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=SUBMITTED,
        )

    def setUp(self):
        self.client.force_login(self.training_manager.person.user)

    def test_list_with_no_archive_visible(self):
        self.admission.archived = True
        self.admission.save()
        response = self.client.post(reverse('archive'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['archives'].object_list, [])

    def test_list_with_archive(self):
        self.admission.archived = True
        self.admission.save()
        PersonTraining(training=self.admission.formation, person=self.training_manager.person).save()
        response = self.client.post(reverse('archive'))
        self.assertEqual(response.status_code, HttpResponse.status_code)
        self.assertCountEqual(response.context['archives'].object_list, [self.admission])

    def test_archive_procedure_denied(self):
        response = self.client.post(
            reverse('archive_procedure', kwargs={'admission_id': self.admission.pk})
        )
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)

    def test_archive_procedure_authorized(self):
        PersonTraining(training=self.admission.formation, person=self.training_manager.person).save()
        response = self.client.post(
            reverse('archive_procedure', kwargs={'admission_id': self.admission.pk})
        )
        self.assertEqual(response.status_code, HttpResponseRedirect.status_code)


class ViewArchiveCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = ContinuingEducationManagerFactory()

    def setUp(self):
        self.client.force_login(self.manager.person.user)
        self.addCleanup(cache.clear)

    def test_cached_filters(self):
        response = self.client.get(reverse('archive'), data={
            'free_text': 'test'
        })
        cached_response = self.client.get(reverse('archive'))
        self.assertEqual(response.wsgi_request.GET['free_text'], cached_response.wsgi_request.GET['free_text'])
