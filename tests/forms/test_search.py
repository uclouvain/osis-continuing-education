##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from unittest import skipUnless

from django.test import TestCase
from django.utils import timezone
from django.utils.translation import pgettext_lazy, gettext as _

from backoffice.settings.base import INSTALLED_APPS
from base.models.enums.entity_type import FACULTY, SCHOOL
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_type import EducationGroupTypeFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.search import ADMISSION_STATE_CHOICES
from continuing_education.forms.search import AdmissionFilterForm, RegistrationFilterForm, FormationFilterForm, \
    ArchiveFilterForm, ALL_CHOICE, ACTIVE, INACTIVE, FORMATION_STATE_CHOICES, NOT_ORGANIZED, ManagerFilterForm, \
    REGISTRATION_STATE_CHOICES, STATE_TO_DISPLAY
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_training import CONTINUING_EDUCATION_TRAINING_TYPES, \
    ContinuingEducationTraining
from continuing_education.models.enums.admission_state_choices import ARCHIVE_STATE_CHOICES
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, ACCEPTED, \
    REGISTRATION_SUBMITTED, ACCEPTED_NO_REGISTRATION_REQUIRED, VALIDATED
from continuing_education.models.person_training import PersonTraining
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory

COUNTRY_NAME_WITHOUT_ACCENT = 'Country - e'
COUNTRY_NAME_WITH_ACCENT = 'Country - é'
CITY_NAME_WITH_ACCENT = 'City - é'


class TestFilterForm(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.current_academic_yr = create_current_academic_year()
        cls.next_academic_yr = AcademicYearFactory(year=cls.current_academic_yr.year + 1)

        cls.start_date = date.today().replace(year=2010)

        cls.fac_1_older_version = EntityVersionFactory(
            acronym="DRT",
            entity_type=FACULTY,
            start_date=date.today().replace(year=2000),
            end_date=cls.start_date - timezone.timedelta(days=1)
        )
        cls.fac_1_version = EntityVersionFactory(
            acronym="DRT_NEW",
            entity_type=FACULTY,
            start_date=cls.start_date,
            end_date=None,
        )
        cls.fac_2_version = EntityVersionFactory(
            acronym="AGRO",
            entity_type=FACULTY,
            start_date=cls.start_date,
            end_date=None,
        )
        cls.fac_3_version_with_child = EntityVersionFactory(
            acronym="ESPO",
            entity_type=FACULTY,
            end_date=None,
            start_date=cls.start_date
        )
        cls.fac_3_child_version = EntityVersionFactory(
            acronym="ESPO_child",
            entity_type=SCHOOL,
            end_date=None,
            start_date=cls.start_date,
            parent=cls.fac_3_version_with_child.entity
        )
        cls.fac_4_version = EntityVersionFactory(
            acronym="ILV",
            entity_type=FACULTY,
            start_date=cls.start_date,
            end_date=None,
        )
        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        cls.education_groups_fac_1_version = [EducationGroupFactory(start_year=cls.current_academic_yr) for _ in range(0, len(letters))]
        cls.education_group_yrs = [
            EducationGroupYearFactory(
                academic_year=cls.next_academic_yr,
                acronym='{}_FORM'.format(letters[index]),
                management_entity=cls.fac_1_version.entity,
                education_group=education_group)
            for index, education_group in enumerate(cls.education_groups_fac_1_version)
        ]

        cls.education_group_on_faculty = EducationGroupFactory(start_year=cls.current_academic_yr)
        cls.education_group_yr_on_faculty = EducationGroupYearFactory(
            academic_year=cls.next_academic_yr,
            acronym='E_FORM_FAC',
            management_entity=cls.fac_3_version_with_child.entity,
            education_group=cls.education_group_on_faculty
        )

        cls.education_group_on_faculty_child = EducationGroupFactory(start_year=cls.current_academic_yr)
        cls.education_group_yr_on_faculty_child = EducationGroupYearFactory(
            academic_year=cls.next_academic_yr,
            acronym='E_FORM_Child',
            management_entity=cls.fac_3_child_version.entity,
            education_group=cls.education_group_on_faculty_child
        )

        cls.admissions_fac_1_version = [
            AdmissionFactory(
                formation=ContinuingEducationTrainingFactory(education_group=cls.education_groups_fac_1_version[index]),
                state=state,
                academic_year=cls.current_academic_yr
            ) for index, state in enumerate([SUBMITTED, REJECTED, WAITING, DRAFT, SUBMITTED])
        ]

        cls.registrations = [
            AdmissionFactory(
                formation=ContinuingEducationTrainingFactory(
                    education_group=cls.education_groups_fac_1_version[len(cls.admissions_fac_1_version) + index],
                ),
                state=state,
                ucl_registration_complete=index == 0,
                payment_complete=index != 0,
                academic_year=cls.current_academic_yr
            ) for index, state in enumerate([ACCEPTED, REGISTRATION_SUBMITTED])
        ]

        cls.education_group_on_fac4 = EducationGroupFactory(start_year=cls.current_academic_yr)
        cls.education_group_yr_on_faculty_child = EducationGroupYearFactory(
            academic_year=cls.next_academic_yr,
            acronym='E_FORM_fac_Child',
            management_entity=cls.fac_4_version.entity,
            education_group=cls.education_group_on_fac4
        )
        cls.registration_validated = AdmissionFactory(
            formation=ContinuingEducationTrainingFactory(
                education_group=cls.education_group_on_fac4),
            state=VALIDATED,
            payment_complete=False,
            ucl_registration_complete=False,
            academic_year=cls.current_academic_yr
            )

        cls.all_registrations_expected = cls.registrations.copy()
        cls.all_registrations_expected.append(cls.registration_validated)

        cls.archived_submitted = AdmissionFactory(
            formation=ContinuingEducationTrainingFactory(
                education_group=cls.education_groups_fac_1_version[7],
            ),
            state=SUBMITTED,
            archived=True,
            academic_year=cls.current_academic_yr
        )

        ed_free_text_acronym = EducationGroupFactory(start_year=cls.current_academic_yr)
        EducationGroupYearFactory(
            acronym="TestText",
            academic_year=cls.next_academic_yr,
            education_group=ed_free_text_acronym
        )
        ed_free_text_title = EducationGroupFactory(start_year=cls.current_academic_yr)
        EducationGroupYearFactory(
            academic_year=cls.next_academic_yr,
            education_group=ed_free_text_title,
            title="bla TestText bla"
        )
        ed = EducationGroupFactory(start_year=cls.current_academic_yr)
        EducationGroupYearFactory(
            academic_year=cls.next_academic_yr,
            education_group=ed
        )
        cls.formation_no_registration_required = ContinuingEducationTrainingFactory(
            education_group=ed,
            registration_required=False,
        )
        cls.persons = [
            PersonFactory(first_name="TestText"),
            PersonFactory(last_name="TestText"),
            PersonFactory(email="TestText@outlook.be")
        ]
        cls.eds = [ed_free_text_title, ed_free_text_acronym]
        cls.admissions_free_text = []
        cls.country_accent = CountryFactory(name=COUNTRY_NAME_WITH_ACCENT)
        cls.country_without_accent = CountryFactory(name=COUNTRY_NAME_WITHOUT_ACCENT)
        cls.form = AdmissionFilterForm()
        cls.registration_form = RegistrationFilterForm()

    def test_queryset_faculty_init(self):
        self.assertListEqual(list(self.form.fields['faculty'].queryset),
                             [self.fac_2_version, self.fac_1_version, self.fac_3_version_with_child, self.fac_4_version])

    def test_queryset_formation_init(self):
        self.assertListEqual(list(self.form.fields['formation'].queryset), [
            a.formation for a in self.admissions_fac_1_version
        ])

    def test_queryset_admission_state_init(self):
        self.assertCountEqual(
            list(self.form.fields['state'].choices),
            [
                ('', pgettext_lazy("plural", "All")),
                ('Waiting', _('Waiting')),
                ('Rejected', _('Rejected')),
                ('Submitted', _('Submitted')),
                ('Draft', _('Draft')),
                ('Accepted (no registration required)', _('Accepted')),
            ])

    def test_queryset_registration_state_init(self):
        self.assertCountEqual(
            list(self.registration_form.fields['state'].choices),
            [
                ('', pgettext_lazy("plural", "All")),
                ('Accepted', _('Accepted')),
                ('Registration submitted',  _('Registration submitted')),
                ('Validated', _('Validated'))
            ]
        )

    def test_queryset_academic_year_init(self):
        expected = [
                ('', pgettext_lazy("plural", "All")),
                (self.current_academic_yr.id, str(self.current_academic_yr)),
                (self.next_academic_yr.id, str(self.next_academic_yr)),
            ]
        self.assertCountEqual(
            list(self.registration_form.fields['academic_year'].choices),
            expected
        )

    def test_get_admissions_no_criteria(self):
        form = AdmissionFilterForm({})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, self.admissions_fac_1_version)

    def test_get_admissions_by_formation_criteria(self):
        form = AdmissionFilterForm({"formation":  self.admissions_fac_1_version[4].formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertListEqual(list(results), [self.admissions_fac_1_version[4]])

    def test_get_admissions_by_faculty_criteria(self):
        form = AdmissionFilterForm({"faculty": self.fac_1_version.id})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, self.admissions_fac_1_version)

    def test_get_admissions_by_faculty_criteria_get_child_too(self):
        an_admission_submitted_1 = AdmissionFactory(
            formation=ContinuingEducationTrainingFactory(
                education_group=self.education_group_on_faculty
            ),
            state=SUBMITTED
        )
        an_admission_submitted_2 = AdmissionFactory(
            formation=ContinuingEducationTrainingFactory(
                education_group=self.education_group_on_faculty_child
            ),
            state=SUBMITTED
        )
        form = AdmissionFilterForm({"faculty": self.fac_3_version_with_child.id})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [an_admission_submitted_1, an_admission_submitted_2])

    def test_get_admissions_by_faculty_and_formation_criteria(self):
        form = AdmissionFilterForm({"faculty": self.fac_1_version.id,
                                    "formation": self.admissions_fac_1_version[0].formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [self.admissions_fac_1_version[0]])

        formation_other = ContinuingEducationTrainingFactory()
        formation_other.save()
        adm = AdmissionFactory(state=random.choice(STATE_TO_DISPLAY))
        form = AdmissionFilterForm({"faculty": self.fac_1_version.id,
                                    "formation": adm.formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [])

    def test_get_admission_by_state(self):
        form = AdmissionFilterForm({"state": [REJECTED]})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [self.admissions_fac_1_version[1]])

    def test_get_admission_by_states(self):
        form = AdmissionFilterForm({"state": [REJECTED, DRAFT]})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [self.admissions_fac_1_version[1], self.admissions_fac_1_version[3]])

    def test_get_admissions_by_free_text(self):
        self._create_admissions_for_free_text_search()
        form = AdmissionFilterForm({"free_text": "testtext"})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, self.admissions_free_text)

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_get_admissions_by_free_text_country(self):
        admission_accent = self._build_admission_with_accent(SUBMITTED, False)
        country_free_text = "Country - e"
        form = AdmissionFilterForm({"free_text": country_free_text})
        form.is_valid()
        results = form.get_admissions()
        self.assertEqual(results.first(), admission_accent)

    def test_get_admission_by_registration_required(self):
        formations_registration_required = ContinuingEducationTraining.objects.filter(registration_required=True)
        admissions_expected = Admission.objects.filter(
            archived=False,
            formation__in=formations_registration_required,
            state__in=[ele for key in ADMISSION_STATE_CHOICES for ele in key])
        form = AdmissionFilterForm({"registration_required": True})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, admissions_expected)

    def test_get_admission_by_no_registration_required(self):
        admission = AdmissionFactory(formation=self.formation_no_registration_required,
                                     state=ACCEPTED_NO_REGISTRATION_REQUIRED)
        form = AdmissionFilterForm({"registration_required": False})
        self.assertTrue(form.is_valid())
        results = form.get_admissions()
        self.assertCountEqual(results, [admission])

    def test_get_registrations_no_criteria(self):
        form = RegistrationFilterForm({})
        self.assertTrue(form.is_valid())

        results = form.get_registrations()
        self.assertCountEqual(results, self.all_registrations_expected)

    def test_get_registrations_by_formation_criteria(self):
        form = RegistrationFilterForm({"formation": self.registrations[0].formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertListEqual(list(results), [self.registrations[0]])

    def test_get_registrations_by_faculty_criteria(self):
        form = RegistrationFilterForm({"faculty": self.fac_1_version.id})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(list(results), self.registrations)

    def test_get_registrations_by_faculty_and_formation_criteria(self):
        form = RegistrationFilterForm({"faculty": self.fac_1_version.id,
                                       "formation": self.registrations[0].formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[0]])

        form = RegistrationFilterForm({"faculty": self.fac_1_version.id,
                                       "formation": self.registration_validated.formation.id})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [])

    def test_get_registrations_by_ucl_registration_complete_criteria(self):
        form = RegistrationFilterForm({"ucl_registration_complete": True})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[0]])

    def test_get_registrations_by_payment_complete(self):
        form = RegistrationFilterForm({"payment_complete": True})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[1]])

        form = RegistrationFilterForm({"payment_complete": True, "ucl_registration_complete": True})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [])

    def test_get_registrations_by_state(self):
        form = RegistrationFilterForm({"state": ACCEPTED})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[0]])

    def test_get_registrations_by_free_text(self):
        self._create_admissions_for_free_text_search()
        for admission in self.admissions_free_text:
            admission.state = ACCEPTED
            admission.save()
        form = RegistrationFilterForm({"free_text": "testtext"})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, self.admissions_free_text)

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_get_registrations_by_free_text_country(self):
        admission_accent = self._build_admission_with_accent(REGISTRATION_SUBMITTED, False)
        country_free_text = "Country - e"
        form = RegistrationFilterForm({"free_text": country_free_text})
        form.is_valid()
        results = form.get_registrations()
        self.assertEqual(results.first(), admission_accent)

    def test_get_registration_received_file_param(self):
        self.registrations[0].registration_file_received = True
        self.registrations[0].save()
        form = RegistrationFilterForm({"registration_file_received": True})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[0]])

        form = RegistrationFilterForm({"registration_file_received": False})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[1], self.registration_validated])

        form = RegistrationFilterForm({})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()
        self.assertCountEqual(results, [self.registrations[0], self.registrations[1], self.registration_validated])

    def test_get_registrations_by_academic_year(self):
        form = RegistrationFilterForm({"academic_year": self.current_academic_yr.id})
        self.assertTrue(form.is_valid())
        results = form.get_registrations()

        self.assertListEqual(list(results), self.all_registrations_expected)

    def test_get_archives_by_free_text(self):
        self._create_admissions_for_free_text_search()
        for admission in self.admissions_free_text:
            admission.archived = True
            admission.save()
        form = ArchiveFilterForm({"free_text": "testtext"})
        self.assertTrue(form.is_valid())
        results = form.get_archives()
        self.assertCountEqual(results, self.admissions_free_text)

    @skipUnless('django.contrib.postgres' in INSTALLED_APPS, 'requires django.contrib.postgres')
    def test_get_archives_by_free_text_country(self):
        admission_accent = self._build_admission_with_accent(REGISTRATION_SUBMITTED, True)
        country_free_text = "Country - e"
        form = ArchiveFilterForm({"free_text": country_free_text})
        form.is_valid()
        results = form.get_archives()
        self.assertEqual(results.first(), admission_accent)

    def test_get_archives_by_state_criteria(self):
        form = ArchiveFilterForm({"state": SUBMITTED})
        self.assertTrue(form.is_valid())
        results = form.get_archives()
        self.assertCountEqual(results, [self.archived_submitted])
        self.assertEqual(form.fields['state'].choices,
                         [ALL_CHOICE] + sorted(ARCHIVE_STATE_CHOICES, key=itemgetter(1)))

    def test_get_archives_state_choices(self):
        form = ArchiveFilterForm(data={})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.fields['state'].choices,
                         [ALL_CHOICE] + sorted(ARCHIVE_STATE_CHOICES, key=itemgetter(1)))

    def _create_admissions_for_free_text_search(self):
        self.admissions_free_text = []
        for person in self.persons:
            self.admissions_free_text.append(
                AdmissionFactory(
                    formation=self.formation_no_registration_required,
                    person_information=ContinuingEducationPersonFactory(
                        person=person
                    ),
                    address=AddressFactory(country=self.country_without_accent),
                    state=SUBMITTED,
                )
            )
        for ed in self.eds:
            self.admissions_free_text.append(
                AdmissionFactory(
                    formation=ContinuingEducationTrainingFactory(
                        education_group=ed
                    ),
                    state=SUBMITTED
                )
            )

    def _build_admission_with_accent(self, a_state, archived):
        address_with_accent = AddressFactory(
            country=self.country_accent,
            city=CITY_NAME_WITH_ACCENT
        )
        admission_accent = AdmissionFactory(
            address=address_with_accent,
            state=a_state,
            archived=archived
        )
        EducationGroupYearFactory(education_group=admission_accent.formation.education_group)
        return admission_accent


class TestFormationFilterForm(TestCase):

    def setUp(self):

        self.title_acronym_12 = 'Acronym 12'
        self.continuing_education_group_type = EducationGroupTypeFactory(
            name=random.choice(CONTINUING_EDUCATION_TRAINING_TYPES)
        )

        self.academic_year = AcademicYearFactory(year=2018)
        self.entity_version = create_entity_version("ENTITY_PREV")
        entity_version_2 = create_entity_version("FAC2")

        self.iufc_education_group_yr_ACRO_10 = EducationGroupYearFactory(
            acronym="ACRO_10",
            education_group_type=self.continuing_education_group_type,
            title='Acronym 10',
            management_entity=self.entity_version.entity,
            academic_year=self.academic_year
        )
        self.iufc_education_group_yr_ACRO_12 = EducationGroupYearFactory(
            acronym="ACRO_12",
            education_group_type=self.continuing_education_group_type,
            title=self.title_acronym_12,
            management_entity=entity_version_2.entity,
            academic_year=self.academic_year
        )

        education_group_not_organized = EducationGroupFactory()
        self.education_group_yr_not_organized = EducationGroupYearFactory(
            acronym="CODE_12",
            education_group_type=self.continuing_education_group_type,
            title="Other title",
            management_entity=self.entity_version.entity,
            education_group=education_group_not_organized,
            academic_year=self.academic_year
        )
        self.active_continuing_education_training = ContinuingEducationTrainingFactory(
            education_group=self.iufc_education_group_yr_ACRO_10.education_group,
            active=True,
        )
        self.inactive_continuing_education_training = ContinuingEducationTrainingFactory(
            education_group=self.iufc_education_group_yr_ACRO_12.education_group,
            active=False,
        )

    def test_get_state_choices(self):
        form = FormationFilterForm(data={})
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.fields['state'].choices, FORMATION_STATE_CHOICES)

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
        self._assert_results_count_equal({'faculty': self.entity_version.id},
                                         [self.iufc_education_group_yr_ACRO_10.education_group,
                                          self.education_group_yr_not_organized.education_group])

    def test_formation_filter_by_free_text(self):
        iufc_education_group_yr_testtext_in_acronym = EducationGroupYearFactory(
            acronym="TestText",
            education_group_type=self.continuing_education_group_type,
            management_entity=self.entity_version.entity,
            academic_year=self.academic_year
        )
        iufc_education_group_yr_testtext_in_title = EducationGroupYearFactory(
            education_group_type=self.continuing_education_group_type,
            title='TestText',
            management_entity=self.entity_version.entity,
            academic_year=self.academic_year
        )
        self._assert_results_count_equal({'free_text': "testtext"},
                                         [iufc_education_group_yr_testtext_in_acronym.education_group,
                                          iufc_education_group_yr_testtext_in_title.education_group])

    def _assert_results_count_equal(self, data, expected_results):
        form = FormationFilterForm(data)
        self.assertTrue(form.is_valid())
        results = form.get_formations()
        self.assertCountEqual(results, expected_results)

    def test_formation_filter_by_multiple(self):
        self._assert_results_count_equal({'acronym': 'ZZZ', 'faculty': self.entity_version.id},
                                         [])
        self._assert_results_count_equal({'acronym': 'ACRO_10', 'faculty': self.entity_version.id},
                                         [self.iufc_education_group_yr_ACRO_10.education_group])


class TestContinuingEducationManagerFilterForm(TestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory(year=2018)
        self.education_group = EducationGroupFactory()
        self.start_date = date.today().replace(year=2010)
        self.faculty = EntityVersionFactory(
            acronym="DRT_NEW",
            entity_type=FACULTY,
            start_date=self.start_date,
            end_date=None,
        )
        EducationGroupYearFactory(
            education_group=self.education_group,
            academic_year=self.academic_year,
            management_entity=self.faculty.entity,
        )

        training_manager_group = GroupFactory(name='continuing_education_training_managers')
        self.training_managers = []
        for _ in range(1, 2):
            training_manager = PersonWithPermissionsFactory(
                'view_admission',
                'change_admission',
            )
            training_manager.user.groups.add(training_manager_group)
            self.training_managers.append(training_manager)

        self.formation = ContinuingEducationTrainingFactory(education_group=self.education_group)
        PersonTraining(person=self.training_managers[0], training=self.formation).save()

        manager_group = GroupFactory(name='continuing_education_managers')
        self.continuing_education_manager = PersonWithPermissionsFactory(
            'view_admission',
            'change_admission',
            'validate_registration'
        )
        self.continuing_education_manager.user.groups.add(manager_group)
        self.client.force_login(self.continuing_education_manager.user)

    def test_managers_no_filter(self):
        self._assert_results_count_equal({}, self.training_managers)

    def test_managers_filter_by_training(self):
        self._assert_results_count_equal({'training': self.formation.id}, [self.training_managers[0]])

    def test_managers_filter_by_person(self):
        self._assert_results_count_equal({'person': self.training_managers[0].id}, [self.training_managers[0]])

    def test_managers_filter_by_faculty(self):
        self._assert_results_count_equal({'faculty': self.faculty.id}, [self.training_managers[0]])

    def test_get_state_choices(self):
        form = RegistrationFilterForm(data={}, user=self.training_managers[0].user)
        self.assertTrue(form.is_valid())
        self.assertCountEqual(form.fields['state'].choices,
                              [ALL_CHOICE] + sorted(REGISTRATION_STATE_CHOICES, key=itemgetter(1)))

    def _assert_results_count_equal(self, data, expected_results):
        form = ManagerFilterForm(data=data)
        self.assertTrue(form.is_valid())
        results = form.get_managers()
        self.assertCountEqual(results, expected_results)


def create_entity_version(an_acronym):
    start_date = date.today().replace(year=2010)
    entity_version = EntityVersionFactory(acronym=an_acronym,
                                          entity_type=FACULTY,
                                          end_date=None,
                                          start_date=start_date)
    return entity_version
