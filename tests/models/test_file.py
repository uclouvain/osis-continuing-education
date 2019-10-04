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

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.translation import gettext as _

from base.models.enums.entity_type import SCHOOL
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.models import admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.exceptions import TooLargeFileSizeException
from continuing_education.models.file import AdmissionFile, MAX_UPLOAD_SIZE
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class TestFile(TestCase):
    def setUp(self):
        self.admission = AdmissionFactory()
        self.file = SimpleUploadedFile(
            name='upload_test.pdf',
            content=str.encode("test_content"),
            content_type="application/pdf",
        )

    def test_file_too_large_exception(self):
        admission_file = AdmissionFile(
            admission=self.admission,
            name='test.pdf',
            path=self.file,
            size=MAX_UPLOAD_SIZE + 1
        )
        self.assertRaises(TooLargeFileSizeException, admission_file.save)
