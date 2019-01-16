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
from base.tests.factories.academic_year import create_current_academic_year, AcademicYearFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory

ANY_REASON = 'Anything'


class TestAdmissionForm(TestCase):

    def test_valid_form(self):
        current_academic_yr = create_current_academic_year()
        next_academic_yr = AcademicYearFactory(year=current_academic_yr.year+1)
        admission = AdmissionFactory(formation=EducationGroupYearFactory(academic_year=next_academic_yr))

        data = admission.__dict__
        data['formation'] = admission.formation.pk
        form = AdmissionForm(data)
        self.assertTrue(form.is_valid(), form.errors)


class TestRejectedAdmissionForm(TestCase):

    def setUp(self):
        self.rejected_admission_other = AdmissionFactory(
            state=REJECTED,
            state_reason=ANY_REASON,
        )
        self.rejected_admission_not_other = AdmissionFactory(
            state=REJECTED,
            state_reason=NOT_ENOUGH_EXPERIENCE,
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
    # person['address']['country'] = country.find_by_id(person["country_id"])
    person['birth_country'] = country.find_by_id(person["birth_country_id"])
    person['citizenship'] = country.find_by_id(person["citizenship_id"])


def convert_dates(person):
    person['birth_date'] = person['birth_date'].strftime('%Y-%m-%d')
    person['high_school_graduation_year'] = person['high_school_graduation_year'].strftime('%Y-%m-%d')
    person['last_degree_graduation_year'] = person['last_degree_graduation_year'].strftime('%Y-%m-%d')
