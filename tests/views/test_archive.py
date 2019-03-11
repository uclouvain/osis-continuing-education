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
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, WAITING
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.views.archive import _switch_archived_state, _mark_as_archived


class ViewArchiveTestCase(TestCase):

    def setUp(self):
        current_acad_year = create_current_academic_year()
        self.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        self.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.formation_1 = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.education_group = EducationGroupFactory()
        education_group_year = EducationGroupYearFactory(education_group=self.education_group)
        self.formation_2 = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )

        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
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
