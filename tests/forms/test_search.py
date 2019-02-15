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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from continuing_education.forms.admission import AdmissionForm, RejectedAdmissionForm
from continuing_education.tests.factories.admission import AdmissionFactory
from reference.models import country
from continuing_education.models.enums.admission_state_choices import REJECTED
from continuing_education.business.enums.rejected_reason import NOT_ENOUGH_EXPERIENCE, OTHER
from base.models.entity_version import EntityVersion
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.forms.search import AdmissionFilterForm
from base.models.academic_year import AcademicYear
from datetime import date
from base.models.enums.entity_type import FACULTY
from django.utils import timezone
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT



class TestAdmissionFilterForm(TestCase):

    def setUp(self):
        current_academic_yr = create_current_academic_year()
        next_academic_yr = AcademicYearFactory(year=current_academic_yr.year + 1)

        self.start_date = date.today().replace(year=2010)

        self.fac_1_older_version = EntityVersionFactory(acronym="DRT",
                                                        entity_type=FACULTY,
                                                        start_date=date.today().replace(year=2000),
                                                        end_date=self.start_date - timezone.timedelta(days=1))

        self.fac_1_version = EntityVersionFactory(acronym="DRT_NEW",
                                                  entity_type=FACULTY,
                                                  end_date=None,
                                                  start_date=self.start_date)

        self.fac_2_version = EntityVersionFactory(acronym="AGRO",
                                                  entity_type=FACULTY,
                                                  end_date=None,
                                                  start_date=self.start_date)

        self.education_group_yr_1 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='A_FORM',
                                                              management_entity=self.fac_1_version.entity)
        self.education_group_yr_2 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='C_FORM')
        self.education_group_yr_3 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='B_FORM',
                                                              management_entity=self.fac_1_version.entity)
        self.education_group_yr_4 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='D_FORM',
                                                              management_entity=self.fac_2_version.entity)
        self.education_group_yr_5_not_admission = EducationGroupYearFactory(academic_year=next_academic_yr,
                                                                            acronym='E_FORM')

        self.admission_submitted_1 = AdmissionFactory(formation=self.education_group_yr_1, state=SUBMITTED)

        self.admission_rejected = AdmissionFactory(formation=self.education_group_yr_2, state=REJECTED)

        self.admission_waiting = AdmissionFactory(formation=self.education_group_yr_3, state=WAITING)

        self.admission_draft = AdmissionFactory(formation=self.education_group_yr_4, state=DRAFT)
        self.admission_submitted_2 = AdmissionFactory(formation=self.education_group_yr_4, state=SUBMITTED)

        self.registration = AdmissionFactory(formation=self.education_group_yr_5_not_admission, state=DRAFT)

    def test_query_set_faculty_init(self):
        form = AdmissionFilterForm()
        self.assertListEqual(list(form.fields['faculty'].queryset), [self.fac_2_version, self.fac_1_version])

    def test_query_set_formation_init(self):
        form = AdmissionFilterForm()
        self.assertListEqual(list(form.fields['formation'].queryset), [self.education_group_yr_1,
                                                                       self.education_group_yr_3,
                                                                       self.education_group_yr_2,
                                                                       self.education_group_yr_4])

    def test_get_admissions_no_criteria(self):
        form = AdmissionFilterForm({})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [self.admission_submitted_1,
                                            self.admission_rejected,
                                            self.admission_waiting,
                                            self.admission_submitted_2])

    def test_get_admissions_by_formation_criteria(self):
        form = AdmissionFilterForm({"formation": self.education_group_yr_4})
        if form.is_valid():
            results = form.get_admissions()
            self.assertListEqual(list(results), [self.admission_submitted_2])

    def test_get_admissions_by_faculty_criteria(self):
        form = AdmissionFilterForm({"faculty": self.fac_1_version})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [self.admission_submitted_1, self.admission_waiting])

    def test_get_admissions_by_faculty_and_formation_criteria(self):
        form = AdmissionFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_1})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [self.admission_submitted_1])

        form = AdmissionFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_2})
        if form.is_valid():
            results = form.get_admissions()
            print(results)
            self.assertCountEqual(results, [])
