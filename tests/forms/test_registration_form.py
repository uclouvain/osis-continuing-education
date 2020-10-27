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

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.group import GroupFactory
from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.enums.groups import MANAGERS_GROUP, TRAINING_MANAGERS_GROUP, STUDENT_WORKERS_GROUP
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class TestRegistrationForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )

    def test_previous_ucl_registration_not_required_if_only_billing(self):
        registration = AdmissionFactory(formation=self.formation)
        data = registration.__dict__
        form = RegistrationForm(data=data, only_billing=True)
        self.assertFalse(form.fields['previous_ucl_registration'].required)

    def test_fields_disabled_for_continuing_training_manager(self):
        training_manager_group = GroupFactory(name=TRAINING_MANAGERS_GROUP)
        manager = PersonWithPermissionsFactory('view_admission', 'change_admission')
        manager.user.groups.add(training_manager_group)

        form = RegistrationForm(data={}, user=manager.user)
        self.assertTrue(form.fields['registration_file_received'].disabled)
        self.assertTrue(form.fields['ucl_registration_complete'].disabled)

    def test_fields_enabled_if_not_continuing_training_manager(self):
        for group in [MANAGERS_GROUP, STUDENT_WORKERS_GROUP]:
            manager_group = GroupFactory(name=group)
            person_not_manager = PersonWithPermissionsFactory('view_admission', 'change_admission')
            person_not_manager.user.groups.add(manager_group)

            form = RegistrationForm(data={}, user=person_not_manager.user)
            self.assertFalse(form.fields['registration_file_received'].disabled)
            self.assertFalse(form.fields['ucl_registration_complete'].disabled)

    def test_only_alphanumeric_characters_for_id_card(self):
        wrong_id = '12-4894'
        registration = AdmissionFactory(formation=self.formation)
        data = registration.__dict__
        data['id_card_number'] = wrong_id
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('id_card_number', form.errors)
        self.assertIn(_('Only alphanumeric characters are allowed.'), form.errors['id_card_number'])

    def test_only_alphanumeric_characters_for_passeport_number(self):
        wrong_id = '12-4894'
        registration = AdmissionFactory(formation=self.formation)
        data = registration.__dict__
        data['passport_number'] = wrong_id
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('passport_number', form.errors)
        self.assertIn(_('Only alphanumeric characters are allowed.'), form.errors['passport_number'])

    def test_only_alphanumeric_characters_for_national_number(self):
        wrong_id = '12-4894'
        registration = AdmissionFactory(formation=self.formation)
        data = registration.__dict__
        data['national_registry_number'] = wrong_id
        form = RegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('national_registry_number', form.errors)
        self.assertIn(_('Only alphanumeric characters are allowed.'), form.errors['national_registry_number'])
