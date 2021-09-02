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
import datetime
import random
from unittest import mock

from django.test import TestCase
from django.utils.translation import gettext_lazy as _

import continuing_education
from base.models.academic_year import AcademicYear
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.business.enums.rejected_reason import NOT_ENOUGH_EXPERIENCE, OTHER
from continuing_education.forms.admission import AdmissionForm, RejectedAdmissionForm, ConditionAcceptanceAdmissionForm, \
    get_academic_years_to_link_qs
from continuing_education.models.enums.admission_state_choices import REJECTED, ACCEPTED, \
    ACCEPTED_NO_REGISTRATION_REQUIRED, REGISTRATION_SUBMITTED, VALIDATED, WAITING, DRAFT, SUBMITTED, CANCELLED, \
    CANCELLED_NO_REGISTRATION_REQUIRED
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.roles.continuing_education_manager import ContinuingEducationManagerFactory
from continuing_education.tests.factories.roles.continuing_education_training_manager import \
    ContinuingEducationTrainingManagerFactory
from reference.models import country

ANY_REASON = 'Anything'


class TestAdmissionForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.current_academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.current_academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.training_manager = ContinuingEducationTrainingManagerFactory(training=cls.formation)
        cls.manager = ContinuingEducationManagerFactory()

    def setUp(self):
        self.client.force_login(self.training_manager.person.user)
        self.admission = AdmissionFactory(formation=self.formation,
                                     academic_year=self.current_academic_year)
        self.data = self.admission.__dict__
        self.data['formation'] = self.admission.formation.pk
        self.data['academic_year'] = self.admission.academic_year.pk

    def test_valid_form_for_managers(self):
        self.client.force_login(self.manager.person.user)
        form = AdmissionForm(data=self.data, user=self.manager.person.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_valid_form_for_training_managers(self):
        form = AdmissionForm(data=self.data, user=self.training_manager.person.user)
        self.assertTrue(form.is_valid(), form.errors)

    def test_not_valid_wrong_phone_format(self):
        wrong_numbers = [
            '1234567891',
            '00+32474945669',
            '0+32474123456',
            '(32)1234567891',
            '0474.12.34.56',
            '0474 123456'
        ]
        short_numbers = ['0032123', '+321234', '0123456']
        long_numbers = ['003212345678912456', '+3212345678912345', '01234567891234567']
        self.data['phone_mobile'] = random.choice(wrong_numbers + short_numbers + long_numbers)
        form = AdmissionForm(data=self.data, user=self.training_manager.person.user)
        self.assertFalse(form.is_valid(), form.errors)
        self.assertDictEqual(
            form.errors,
            {
                'phone_mobile': [
                    _("Phone number must start with 0 or 00 or '+' followed by at least "
                      "7 digits and up to 15 digits.")
                ],
            }
        )

    def test_participant_required_fields(self):
        self.client.force_login(self.manager.person.user)
        form = AdmissionForm(data=self.data, user=self.manager.person.user)
        admission_participant_required_fields = [
            'citizenship', 'phone_mobile', 'high_school_diploma', 'last_degree_level',
            'last_degree_field', 'last_degree_institution', 'last_degree_graduation_year',
            'professional_status', 'current_occupation', 'current_employer', 'activity_sector', 'motivation',
            'professional_personal_interests', 'formation', 'email',
        ]
        for required_field in admission_participant_required_fields:
            with self.subTest(required_field=required_field):
                self.assertEqual(
                    form.fields[required_field].widget.attrs['class'],
                    'participant_required'
                )

    def test_manager_email_field_required(self):
        self.client.force_login(self.manager.person.user)
        form = AdmissionForm(data=self.data, user=self.manager.person.user)
        self.assertTrue(form.fields['email'].required)

    def test_academic_year_field_required(self):
        self.client.force_login(self.manager.person.user)
        for state in [ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED, REGISTRATION_SUBMITTED, VALIDATED]:
            with self.subTest(state=state):
                self.admission.state = state
                self.admission.save()
                form = AdmissionForm(data=self.data, user=self.manager.person.user, instance=self.admission)
                self.assertTrue(form.fields['academic_year'].required)

    def test_academic_year_field_not_required(self):
        self.client.force_login(self.manager.person.user)
        for state in [REJECTED, WAITING, DRAFT, SUBMITTED, CANCELLED, CANCELLED_NO_REGISTRATION_REQUIRED]:
            with self.subTest(state=state):
                self.admission.state = state
                self.admission.save()
                form = AdmissionForm(data=self.data, user=self.manager.person.user, instance=self.admission)
                self.assertFalse(form.fields['academic_year'].required)


class TestRejectedAdmissionForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.rejected_admission_other = AdmissionFactory(
            state=REJECTED,
            state_reason=ANY_REASON,
            formation=cls.formation
        )
        cls.rejected_admission_not_other = AdmissionFactory(
            state=REJECTED,
            state_reason=NOT_ENOUGH_EXPERIENCE,
            formation=cls.formation
        )

    def test_init_rejected_init_not_other(self):
        form = RejectedAdmissionForm(None, instance=self.rejected_admission_not_other)

        self.assertEqual(form.fields['other_reason'].initial, '')
        self.assertEqual(form.fields['rejected_reason'].initial, NOT_ENOUGH_EXPERIENCE)
        self.assertTrue(form.fields['other_reason'].disabled)

    def test_init_rejected_init_other(self):
        form = RejectedAdmissionForm(None, instance=self.rejected_admission_other)

        self.assertEqual(form.fields['other_reason'].initial, ANY_REASON)
        self.assertEqual(form.fields['rejected_reason'].initial, OTHER)

        self.assertFalse(form.fields['other_reason'].disabled)

    def test_save_other_reason(self):
        data = self.rejected_admission_other.__dict__
        data['rejected_reason'] = OTHER
        new_reason = "{} else".format(ANY_REASON)
        data['other_reason'] = new_reason

        form = RejectedAdmissionForm(data, instance=self.rejected_admission_other)
        obj_updated = form.save()
        self.assertEqual(obj_updated.state, REJECTED)
        self.assertEqual(obj_updated.state_reason, new_reason)

    def test_save_not_other_reason(self):
        data = self.rejected_admission_not_other.__dict__
        data['rejected_reason'] = NOT_ENOUGH_EXPERIENCE

        form = RejectedAdmissionForm(data, instance=self.rejected_admission_not_other)
        obj_updated = form.save()
        self.assertEqual(obj_updated.state, REJECTED)
        self.assertEqual(obj_updated.state_reason, NOT_ENOUGH_EXPERIENCE)


def convert_countries(person):
    person['birth_country'] = country.find_by_id(person["birth_country_id"])
    person['citizenship'] = country.find_by_id(person["citizenship_id"])


def convert_dates(person):
    person['birth_date'] = person['birth_date'].strftime('%Y-%m-%d')
    person['high_school_graduation_year'] = person['high_school_graduation_year'].strftime('%Y-%m-%d')
    person['last_degree_graduation_year'] = person['last_degree_graduation_year'].strftime('%Y-%m-%d')


class TestAcceptedAdmissionForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = create_current_academic_year()
        cls.next_academic_year = AcademicYearFactory(year=cls.academic_year.year+1)
        AcademicYearFactory.produce(base_year=cls.academic_year.year, number_past=10, number_future=10)

        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        cls.accepted_admission_without_condition = AdmissionFactory(
            state=ACCEPTED,
            formation=cls.formation
        )
        cls.accepted_admission_with_condition = AdmissionFactory(
            state=ACCEPTED,
            condition_of_acceptance="Condition",
            formation=cls.formation
        )

    def test_init_accepted_init_with_condition(self):
        form = ConditionAcceptanceAdmissionForm(None, instance=self.accepted_admission_with_condition)

        self.assertEqual(form.fields['condition_of_acceptance'].initial,
                         self.accepted_admission_with_condition.condition_of_acceptance)
        self.assertFalse(form.fields['condition_of_acceptance'].disabled)
        self.assertTrue(form.fields['condition_of_acceptance_existing'].initial)

    def test_init_form_academic_year_choice_before_switch_date(self):
        date_patcher = mock.patch.object(
            continuing_education.forms.admission, 'date',
            mock.Mock(wraps=datetime.date)
        )
        mocked_date = date_patcher.start()
        mocked_date.today.return_value = datetime.date(2020, 9, 14)
        form = ConditionAcceptanceAdmissionForm(None)
        self.assertCountEqual(
            form.fields['academic_year'].choices.queryset,
            AcademicYear.objects.filter(year__in=[2019, 2020])
        )
        self.addCleanup(date_patcher.stop)

    def test_init_form_academic_year_choice_after_switch_date(self):
        date_patcher = mock.patch.object(
            continuing_education.forms.admission, 'date',
            mock.Mock(wraps=datetime.date)
        )
        mocked_date = date_patcher.start()
        mocked_date.today.return_value = datetime.date(2020, 9, 15)
        form = ConditionAcceptanceAdmissionForm(None)
        self.assertCountEqual(
            form.fields['academic_year'].choices.queryset,
            AcademicYear.objects.filter(year__in=[2020, 2021])
        )
        self.addCleanup(date_patcher.stop)

    def test_init_accepted_init_without_condition(self):
        form = ConditionAcceptanceAdmissionForm(None, instance=self.accepted_admission_without_condition)

        self.assertEqual(form.fields['condition_of_acceptance'].initial, '')
        self.assertTrue(form.fields['condition_of_acceptance'].disabled)
        self.assertFalse(form.fields['condition_of_acceptance_existing'].initial)

    def test_save_with_condition(self):
        data = self.accepted_admission_with_condition.__dict__

        data['condition_of_acceptance_existing'] = True
        data['condition_of_acceptance'] = 'New Condition'
        data['academic_year'] = get_academic_years_to_link_qs().first().pk

        form = ConditionAcceptanceAdmissionForm(data, instance=self.accepted_admission_with_condition)
        obj_updated = form.save()
        self.assertEqual(obj_updated.state, ACCEPTED)
        self.assertEqual(obj_updated.condition_of_acceptance, 'New Condition')

    def test_save_without_condition(self):
        data = self.accepted_admission_without_condition.__dict__

        data['condition_of_acceptance_existing'] = False
        data['condition_of_acceptance'] = 'If false before no condition possible'
        data['academic_year'] = get_academic_years_to_link_qs().first().pk

        form = ConditionAcceptanceAdmissionForm(data, instance=self.accepted_admission_without_condition)
        obj_updated = form.save()
        self.assertEqual(obj_updated.state, ACCEPTED)
        self.assertEqual(obj_updated.condition_of_acceptance, '')
