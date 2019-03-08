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
import random
from datetime import date
from operator import itemgetter

from django.test import TestCase

from django.utils import timezone

from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from base.models.enums.entity_type import FACULTY, SCHOOL
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.forms.search import AdmissionFilterForm, RegistrationFilterForm, FormationFilterForm, \
    ArchiveFilterForm, ALL_CHOICE, ACTIVE, INACTIVE, FORMATION_STATE_CHOICES, NOT_ORGANIZED
from continuing_education.models.enums.admission_state_choices import ARCHIVE_STATE_CHOICES
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, ACCEPTED, \
    REGISTRATION_SUBMITTED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.models.continuing_education_training import CONTINUING_EDUCATION_TRAINING_TYPES
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class TestFilterForm(TestCase):

    def setUp(self):
        self.current_academic_yr = create_current_academic_year()
        next_academic_yr = AcademicYearFactory(year=self.current_academic_yr.year + 1)

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

        self.fac_3_version_with_child = EntityVersionFactory(acronym="ESPO",
                                                             entity_type=FACULTY,
                                                             end_date=None,
                                                             start_date=self.start_date)
        self.fac_3_child_version = EntityVersionFactory(acronym="ESPO_child",
                                                        entity_type=SCHOOL,
                                                        end_date=None,
                                                        start_date=self.start_date,
                                                        parent=self.fac_3_version_with_child.entity)

        self.education_group_yr_1 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='A_FORM',
                                                              management_entity=self.fac_1_version.entity)
        self.education_group_yr_2 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='C_FORM')
        self.education_group_yr_3 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='B_FORM',
                                                              management_entity=self.fac_1_version.entity)
        self.education_group_yr_4 = EducationGroupYearFactory(academic_year=next_academic_yr, acronym='D_FORM',
                                                              management_entity=self.fac_2_version.entity)
        self.education_group_yr_on_faculty = EducationGroupYearFactory(
            academic_year=next_academic_yr,
            acronym='E_FORM',
            management_entity=self.fac_3_version_with_child.entity
        )
        self.education_group_yr_on_faculty_child = EducationGroupYearFactory(
            academic_year=next_academic_yr,
            acronym='E_FORM_Child',
            management_entity=self.fac_3_child_version.entity
        )

        self.admission_submitted_1 = AdmissionFactory(formation=self.education_group_yr_1, state=SUBMITTED)

        self.admission_rejected = AdmissionFactory(formation=self.education_group_yr_2, state=REJECTED)

        self.admission_waiting = AdmissionFactory(formation=self.education_group_yr_3, state=WAITING)

        self.admission_draft = AdmissionFactory(formation=self.education_group_yr_4, state=DRAFT)
        self.admission_submitted_2 = AdmissionFactory(formation=self.education_group_yr_4, state=SUBMITTED)

        self.registration_accepted = AdmissionFactory(formation=self.education_group_yr_on_faculty,
                                                      state=ACCEPTED,
                                                      ucl_registration_complete=True,
                                                      payment_complete=False)
        self.registration_submitted = AdmissionFactory(formation=self.education_group_yr_1,
                                                       state=REGISTRATION_SUBMITTED,
                                                       ucl_registration_complete=False,
                                                       payment_complete=True)
        self.archived_submitted = AdmissionFactory(formation=self.education_group_yr_1,
                                                   state=SUBMITTED,
                                                   archived=True)

    def test_queryset_faculty_init(self):
        form = AdmissionFilterForm()
        self.assertListEqual(list(form.fields['faculty'].queryset),
                             [self.fac_2_version, self.fac_1_version, self.fac_3_version_with_child])

    def test_queryset_formation_init(self):
        form = AdmissionFilterForm()
        self.assertListEqual(list(form.fields['formation'].queryset), [self.education_group_yr_1,
                                                                       self.education_group_yr_3,
                                                                       self.education_group_yr_2,
                                                                       self.education_group_yr_4])

    def test_queryset_registration_state_init(self):
        form = RegistrationFilterForm()
        self.assertListEqual(list(form.fields['state'].choices),
                             [('', pgettext_lazy("plural", "All")),
                              ('Accepted', _('Accepted')),
                              ('Registration submitted',  _('Registration submitted')),
                              ('Validated', _('Validated'))
                              ]
                             )

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

    def test_get_admissions_by_faculty_criteria_get_child_too(self):
        an_admission_submitted_1 = AdmissionFactory(formation=self.education_group_yr_on_faculty,
                                                    state=SUBMITTED)
        an_admission_submitted_2 = AdmissionFactory(formation=self.education_group_yr_on_faculty_child,
                                                    state=SUBMITTED)

        form = AdmissionFilterForm({"faculty": self.fac_3_version_with_child})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [an_admission_submitted_1, an_admission_submitted_2])

    def test_get_admissions_by_faculty_and_formation_criteria(self):
        form = AdmissionFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_1})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [self.admission_submitted_1])

        form = AdmissionFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_2})
        if form.is_valid():
            results = form.get_admissions()
            self.assertCountEqual(results, [])

    def test_get_registrations_no_criteria(self):
        form = RegistrationFilterForm({})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_accepted,
                                            self.registration_submitted])

    def test_get_registrations_by_formation_criteria(self):
        form = RegistrationFilterForm({"formation": self.education_group_yr_1})
        if form.is_valid():
            results = form.get_registrations()
            self.assertListEqual(list(results), [self.registration_submitted])

    def test_get_registrations_by_faculty_criteria(self):
        form = RegistrationFilterForm({"faculty": self.fac_1_version})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_submitted])

    def test_get_registrations_by_faculty_and_formation_criteria(self):
        form = RegistrationFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_1})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_submitted])

        form = RegistrationFilterForm({"faculty": self.fac_1_version, "formation": self.education_group_yr_on_faculty})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [])

    def test_get_registrations_by_ucl_registration_complete_criteria(self):
        form = RegistrationFilterForm({"ucl_registration_complete": True})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_accepted])

    def test_get_registrations_by_payment_complete(self):
        form = RegistrationFilterForm({"payment_complete": True})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_submitted])

        form = RegistrationFilterForm({"payment_complete": True, "ucl_registration_complete": True})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [])

    def test_get_registrations_by_state(self):
        form = RegistrationFilterForm({"state": ACCEPTED})
        if form.is_valid():
            results = form.get_registrations()
            self.assertCountEqual(results, [self.registration_accepted])

    def test_get_archives_by_state_criteria(self):
        form = ArchiveFilterForm({"state": SUBMITTED})
        if form.is_valid():
            results = form.get_archives()
            self.assertCountEqual(results, [self.archived_submitted])
            self.assertEqual(form.fields['state'].choices,
                             [ALL_CHOICE] + sorted(ARCHIVE_STATE_CHOICES, key=itemgetter(1)))

    def test_get_archives_state_choices(self):
        form = ArchiveFilterForm()
        if form.is_valid():
            self.assertEqual(form.fields['state'].choices,
                             [ALL_CHOICE] + sorted(ARCHIVE_STATE_CHOICES, key=itemgetter(1)))


class TestFormationFilterForm(TestCase):

    def setUp(self):

        self.title_acronym_12 = 'Acronym 12'
        continuing_education_group_type = EducationGroupTypeFactory(
            name=random.choice(CONTINUING_EDUCATION_TRAINING_TYPES)
        )

        self.entity_version = create_entity_version("ENTITY_PREV")
        entity_version_2 = create_entity_version("ENTITY_PREV2")

        self.iufc_education_group_yr_ACRO_10 = EducationGroupYearFactory(
            acronym="ACRO_10",
            education_group_type=continuing_education_group_type,
            title='Acronym 10',
            management_entity=self.entity_version.entity
        )
        self.iufc_education_group_yr_ACRO_12 = EducationGroupYearFactory(
            acronym="ACRO_12",
            education_group_type=continuing_education_group_type,
            title=self.title_acronym_12,
            management_entity=entity_version_2.entity
        )

        education_group_not_organized = EducationGroupFactory()
        self.education_group_yr_not_organized = EducationGroupYearFactory(
            acronym="CODE_12",
            education_group_type=continuing_education_group_type,
            title="Other title",
            management_entity=self.entity_version.entity,
            education_group=education_group_not_organized)
        self.active_continuing_education_training = ContinuingEducationTrainingFactory(
            education_group=self.iufc_education_group_yr_ACRO_10.education_group,
            active=True,
        )
        self.inactive_continuing_education_training = ContinuingEducationTrainingFactory(
            education_group=self.iufc_education_group_yr_ACRO_12.education_group,
            active=False,
        )

    def test_get_state_choices(self):
        form = FormationFilterForm()
        if form.is_valid():
            self.assertCountEqual(form.fields['state'].queryset, FORMATION_STATE_CHOICES)

    def test_formation_filter_by_state(self):

        self._assert_results_count_equal({'state': ACTIVE},
                                         [self.active_continuing_education_training.education_group])
        self._assert_results_count_equal({'state': INACTIVE},
                                         [self.inactive_continuing_education_training.education_group])

        self._assert_results_count_equal({'state': NOT_ORGANIZED},
                                         [self.education_group_yr_not_organized.education_group])

    def test_formation_filter_by_acronym(self):
        self._assert_results_count_equal({'acronym': 'ACRO'},
                                         [self.iufc_education_group_yr_ACRO_10.education_group,
                                          self.iufc_education_group_yr_ACRO_12.education_group])
        self._assert_results_count_equal({'acronym': 'ACRO_12'},
                                         [self.iufc_education_group_yr_ACRO_12.education_group])

    def test_formation_filter_by_title(self):
        self._assert_results_count_equal({'title': self.title_acronym_12},
                                         [self.iufc_education_group_yr_ACRO_12.education_group])

    def test_formation_filter_by_faculty(self):
        self._assert_results_count_equal({'faculty': self.entity_version},
                                         [self.iufc_education_group_yr_ACRO_10.education_group])

    def _assert_results_count_equal(self, data, expected_results):
        form = FormationFilterForm(data)
        if form.is_valid():
            results = form.get_formations()
            self.assertCountEqual(results, expected_results)

    def test_formation_filter_by_multiple(self):
        self._assert_results_count_equal({'acronym': 'ZZZ', 'faculty': self.entity_version},
                                         [])
        self._assert_results_count_equal({'acronym': 'ACRO_10', 'faculty': self.entity_version},
                                         [self.iufc_education_group_yr_ACRO_10.education_group])


def create_entity_version(an_acronym):
    start_date = date.today().replace(year=2010)
    entity_version = EntityVersionFactory(acronym=an_acronym,
                                          entity_type=FACULTY,
                                          end_date=None,
                                          start_date=start_date)
    return entity_version
