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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

from base.models.enums import entity_type
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.user import UserFactory
from continuing_education.business.xls.xls_archive import ARCHIVE_TITLES, XLS_DESCRIPTION, XLS_FILENAME, \
    WORKSHEET_TITLE, create_xls, prepare_xls_content
from continuing_education.forms.search import ArchiveFilterForm
from continuing_education.models.enums.admission_state_choices import SUBMITTED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from osis_common.document import xls_build

FACULTY_ACRONYM = "AGRO"


class TestArchiveXls(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        current_acad_year = create_current_academic_year()
        cls.next_acad_year = AcademicYearFactory(year=current_acad_year.year + 1)
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=current_acad_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.entity_version = EntityVersionFactory(
            entity=cls.formation.management_entity,
            acronym=FACULTY_ACRONYM,
            entity_type=entity_type.FACULTY
        )
        cls.admission = AdmissionFactory(
            formation=cls.formation,
            state=SUBMITTED,
            archived=True
        )

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(prepare_xls_content([]), [])

    def test_generate_xls_data_with_an_archive(self):
        a_form = ArchiveFilterForm({"faculty": self.entity_version.id})
        self.assertTrue(a_form.is_valid())
        found_archives = a_form.get_archives()
        create_xls(self.user, found_archives, None)

        xls_data = [[
            self.admission.person_information.person.first_name,
            self.admission.person_information.person.last_name,
            self.admission.email,
            self.admission.formation,
            self.entity_version.entity,
            _(SUBMITTED)
        ]]

        expected_argument = _generate_xls_build_parameter(xls_data, self.user)

        self.assertEqual(expected_argument['list_description'], _('Archives list'))
        self.assertEqual(expected_argument['filename'], _('Archives_list'))
        self.assertEqual(expected_argument['username'], self.user.username)
        self.assertEqual(expected_argument['data'][0]['content'], xls_data)
        self.assertEqual(expected_argument['data'][0]['header_titles'], ARCHIVE_TITLES)
        self.assertEqual(expected_argument['data'][0]['worksheet_title'], _('Archives list'))


def _generate_xls_build_parameter(xls_data, user):
    return {
        xls_build.LIST_DESCRIPTION_KEY: XLS_DESCRIPTION,
        xls_build.FILENAME_KEY: XLS_FILENAME,
        xls_build.USER_KEY: user.username,
        xls_build.WORKSHEETS_DATA: [{
            xls_build.CONTENT_KEY: xls_data,
            xls_build.HEADER_TITLES_KEY: ARCHIVE_TITLES,
            xls_build.WORKSHEET_TITLE_KEY: WORKSHEET_TITLE,
            xls_build.STYLED_CELLS: None,
            xls_build.FONT_ROWS: None,
        }]
    }
