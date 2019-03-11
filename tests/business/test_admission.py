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

from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.business.admission import _get_formatted_admission_data
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory


class TestAdmission(TestCase):
    def test_get_formatted_admission_data(self):
        education_group = EducationGroupFactory()
        EducationGroupYearFactory(education_group=education_group)
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
