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

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from continuing_education.forms.search import FormationFilterForm
from continuing_education.business.xls.xls_formation import TITLES, XLS_DESCRIPTION, XLS_FILENAME,  WORKSHEET_TITLE, \
    create_xls, prepare_xls_content
from osis_common.document import xls_build
from base.tests.factories.user import UserFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.models.enums import entity_type
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory

ACRONYM = "ACRO"


class TestFormationXls(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.entity_version = EntityVersionFactory(
            entity_type=entity_type.FACULTY

        )
        self.education_group_yr = EducationGroupYearFactory(
            acronym="ACRO",
            management_entity=self.entity_version.entity
        )
        self.formation = ContinuingEducationTrainingFactory(education_group=self.education_group_yr.education_group,
                                                            active=True)

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(prepare_xls_content([]), [])

    def test_generate_xls_data_with_a_formation(self):
        a_form = FormationFilterForm({"acronym": ACRONYM})
        self.assertTrue(a_form.is_valid())
        found_formations = a_form.get_formations()
        create_xls(self.user, found_formations, None)

        xls_data = [[
            ACRONYM,
            self.education_group_yr.management_entity.most_recent_acronym,
            self.education_group_yr.title,
            _('Active')
        ]]

        expected_argument = _generate_xls_build_parameter(xls_data, self.user)

        self.assertEqual(expected_argument['list_description'], _('Formations list'))
        self.assertEqual(expected_argument['filename'], _('Formations_list'))
        self.assertEqual(expected_argument['username'], self.user.username)
        self.assertEqual(expected_argument['data'][0]['content'], xls_data)
        self.assertEqual(expected_argument['data'][0]['header_titles'], TITLES)
        self.assertEqual(expected_argument['data'][0]['worksheet_title'], _('Formations list'))


def _generate_xls_build_parameter(xls_data, user):
    return {
        xls_build.LIST_DESCRIPTION_KEY: XLS_DESCRIPTION,
        xls_build.FILENAME_KEY: XLS_FILENAME,
        xls_build.USER_KEY: user.username,
        xls_build.WORKSHEETS_DATA: [{
            xls_build.CONTENT_KEY: xls_data,
            xls_build.HEADER_TITLES_KEY: TITLES,
            xls_build.WORKSHEET_TITLE_KEY: WORKSHEET_TITLE,
            xls_build.STYLED_CELLS: None,
            xls_build.COLORED_ROWS: None,
        }]
    }
