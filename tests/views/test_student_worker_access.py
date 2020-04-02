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
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.roles.continuing_education_student_worker import \
    ContinuingEducationStudentWorkerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory


class ViewsLimitedForStudentWorker(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = ContinuingEducationStudentWorkerFactory()
        cls.training_manager = ContinuingEducationTrainingManagerFactory()
        cls.admission = AdmissionFactory()

        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year,
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group,
            active=True
        )

    def setUp(self):
        self.client.force_login(self.student.person.user)

    def test_get_access(self):
        urls = [
            reverse('admission'),
            reverse('send_invoice_notification_mail', args=[self.admission.id]),
            reverse('admission_new', ),
            reverse('admission_edit', args=[self.admission.id]),
            reverse('validate_field', args=[self.admission.id]),
            reverse('archive'),
            reverse('unarchives_procedure'),
            reverse('archive_procedure', args=[self.admission.id]),
            reverse('formation'),
            reverse('update_formations'),
            reverse('list_managers'),
            reverse(
                'delete_continuing_education_training_manager',
                args=[self.formation.id, self.training_manager.person.id]
            ),
            reverse('prospects'),
            reverse('registration_edit', args=[self.admission.id]),
            reverse('formation_detail', args=[1]),
            reverse('cancelled_files'),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertTemplateUsed(response, 'access_denied.html')

    def test_post_access(self):
        urls = [
            reverse('mark_diplomas_produced'),
        ]
        for url in urls:
            response = self.client.post(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertTemplateUsed(response, 'access_denied.html')
