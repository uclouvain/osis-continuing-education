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

from continuing_education.business.xls.xls_prospect import _prepare_xls_content, _get_titles
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.prospect import ProspectFactory
from django.test.utils import override_settings


class TestProspectXls(TestCase):

    def test_prepare_xls_content_no_data(self):
        self.assertEqual(_prepare_xls_content([]), [])

    def test_prepare_xls_content(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_groups = [EducationGroupFactory() for _ in range(1, 5)]

        acronyms = ['AAA', 'BBA', 'CAA', 'INFO2M', 'SBIM2M']
        for index, education_group in enumerate(self.education_groups):
            EducationGroupYearFactory(
                acronym=acronyms[index],
                education_group=education_group,
                academic_year=self.academic_year
            )

        prospects = [
            ProspectFactory(
                name="Martin{}".format(idx),
                formation=ContinuingEducationTrainingFactory(
                    education_group=education_group,

                )
            ) for idx, education_group in enumerate(self.education_groups)
            ]

        expected_data = [
            [prospect.name,
             prospect.first_name,
             prospect.city,
             prospect.email,
             prospect.phone_number,
             prospect.formation] for prospect in prospects
            ]

        self.assertCountEqual(_prepare_xls_content(prospects), expected_data)

    @override_settings(LANGUAGES=[('en', 'English'), ], LANGUAGE_CODE='en')
    def test_get_titles_en(self):
        self.assertCountEqual(_get_titles(), ['Name',
                                              'First name',
                                              'City',
                                              'Email',
                                              'Phone number',
                                              'Formation'])

    @override_settings(LANGUAGES=[('fr-be', 'French'), ], LANGUAGE_CODE='fr-be')
    def test_get_titles_fr(self):
        self.assertCountEqual(_get_titles(), ['Nom',
                                              'Prénom',
                                              'Ville',
                                              'Courriel',
                                              'Numéro de téléphone',
                                              'Formation'])
