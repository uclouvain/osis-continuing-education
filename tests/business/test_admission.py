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
from django.utils.translation import gettext as _

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.person import PersonFactory
from continuing_education.business.admission import _get_formatted_admission_data, _get_managers_mails
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person_training import PersonTrainingFactory


class TestAdmission(TestCase):
    def test_get_formatted_admission_data(self):
        academic_year = AcademicYearFactory(year=2018)
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=education_group,
            academic_year=academic_year
        )
        training = ContinuingEducationTrainingFactory(education_group=education_group)
        admission = AdmissionFactory(formation=training)
        expected_list = [
            "{} : {}".format(_('Last name'), admission.person_information.person.last_name),
            "{} : {}".format(_('First name'), admission.person_information.person.first_name),
            "{} : {}".format(_('Formation'), admission.formation.acronym),
            "{} : {}".format(_('High school diploma'), _('Yes') if admission.high_school_diploma else _('No')),
            "{} : {}".format(_('High school graduation year'), admission.high_school_graduation_year),
            "{} : {}".format(_('Last degree level'), admission.last_degree_level),
            "{} : {}".format(_('Last degree field'), admission.last_degree_field),
            "{} : {}".format(_('Last degree institution'), admission.last_degree_institution),
            "{} : {}".format(_('Last degree graduation year'), admission.last_degree_graduation_year),
            "{} : {}".format(_('Other educational background'), admission.other_educational_background),
            "{} : {}".format(_('Professional status'), admission.professional_status),
            "{} : {}".format(_('Current occupation'), admission.current_occupation),
            "{} : {}".format(_('Current employer'), admission.current_employer),
            "{} : {}".format(_('Activity sector'), admission.activity_sector),
            "{} : {}".format(_('Past professional activities'), admission.past_professional_activities),
            "{} : {}".format(_('Motivation'), admission.motivation),
            "{} : {}".format(_('Professional impact'), admission.professional_impact),
            "{} : {}".format(_('State'), _(admission.state)),
        ]
        self.assertListEqual(
            _get_formatted_admission_data(admission),
            expected_list
        )

    def test_get_managers_mail(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(education_group=ed)
        manager = PersonFactory(last_name="AAA")
        manager_2 = PersonFactory(last_name="BBB")
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        PersonTrainingFactory(person=manager, training=cet)
        PersonTrainingFactory(person=manager_2, training=cet)
        admission = AdmissionFactory(formation=cet)
        expected_mails = "{} {}{} ".format(manager.email, _(" or "), manager_2.email)

        self.assertEqual(_get_managers_mails(admission.formation), expected_mails)
