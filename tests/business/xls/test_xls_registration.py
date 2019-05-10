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
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from base.models.enums import entity_type
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.user import UserFactory
from continuing_education.business.xls.xls_registration import _get_titles, XLS_DESCRIPTION, XLS_FILENAME, \
    WORKSHEET_TITLE, create_xls_registration, prepare_xls_content
from continuing_education.forms.search import RegistrationFilterForm
from continuing_education.models.enums.admission_state_choices import ACCEPTED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from osis_common.document import xls_build

FACULTY_ACRONYM = "AGRO"


class TestRegistrationXls(TestCase):

    def setUp(self):
        self.user = UserFactory()
        current_academic_yr = create_current_academic_year()
        self.next_academic_yr = AcademicYearFactory(year=current_academic_yr.year + 1)
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year
        )
        self.formation = ContinuingEducationTrainingFactory(
            education_group=self.education_group
        )
        self.entity_version = EntityVersionFactory(
            entity=self.formation.management_entity,
            acronym=FACULTY_ACRONYM,
            entity_type=entity_type.FACULTY

        )
        self.registration = AdmissionFactory(
            formation=self.formation,
            state=ACCEPTED,
            ucl_registration_complete=True,
            payment_complete=False,
        )

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(prepare_xls_content([]), [])

    def test_generate_xls_data_with_an_admission(self):
        a_form = RegistrationFilterForm({"faculty": self.entity_version.id})
        self.assertTrue(a_form.is_valid())
        found_registrations = a_form.get_registrations()
        create_xls_registration(self.user, found_registrations, None)

        xls_data = [[
            self.registration.person_information.person.first_name,
            self.registration.person_information.person.last_name,
            self.registration.email,
            self.registration.formation,
            self.entity_version.entity,
            _('Yes'),
            _('No'),
            self.registration.state
        ]]

        expected_argument = _generate_xls_build_parameter(xls_data, self.user)

        self.assertEqual(expected_argument['list_description'], _('Registrations list'))
        self.assertEqual(expected_argument['filename'], _('Registrations_list'))
        self.assertEqual(expected_argument['username'], self.user.username)
        self.assertEqual(expected_argument['data'][0]['content'], xls_data)
        self.assertEqual(expected_argument['data'][0]['header_titles'], _get_titles())
        self.assertEqual(expected_argument['data'][0]['worksheet_title'], _('Registrations list'))


def _generate_xls_build_parameter(xls_data, user):
    return {
        xls_build.LIST_DESCRIPTION_KEY: XLS_DESCRIPTION,
        xls_build.FILENAME_KEY: XLS_FILENAME,
        xls_build.USER_KEY: user.username,
        xls_build.WORKSHEETS_DATA: [{
            xls_build.CONTENT_KEY: xls_data,
            xls_build.HEADER_TITLES_KEY: _get_titles(),
            xls_build.WORKSHEET_TITLE_KEY: WORKSHEET_TITLE,
            xls_build.STYLED_CELLS: None,
            xls_build.COLORED_ROWS: None,
        }]
    }
