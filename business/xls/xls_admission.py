##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.utils.translation import ugettext_lazy as _

from base.business.xls import get_name_or_username
from continuing_education.business.xls.xls_common import form_filters
from osis_common.document import xls_build

XLS_DESCRIPTION = _('Admissions list')
XLS_FILENAME = _('Admissions_list')
WORKSHEET_TITLE = _('Admissions list')


def create_xls(user, admission_list, form):
    filters = form_filters(form)

    working_sheets_data = prepare_xls_content(admission_list)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: _get_titles(),
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(admission_list):
    return [extract_xls_data_from_admission(admission) for admission in admission_list]


def extract_xls_data_from_admission(admission):
    return [
        admission.person_information.person.last_name,
        admission.person_information.person.first_name,
        admission.email,
        _(admission.state) if admission.state else '',
        admission.person_information.person.get_gender_display() if admission.person_information.person.gender else '',
        admission.citizenship.name if admission.citizenship else '',
        admission.person_information.person.birth_date,
        admission.person_information.birth_location,
        admission.person_information.birth_country.name if admission.person_information.birth_country else '',
        admission.phone_mobile,
        admission.complete_contact_address,
        _('Yes') if admission.high_school_diploma else _('No'),
        admission.high_school_graduation_year,
        admission.last_degree_level,
        admission.last_degree_institution,
        admission.last_degree_graduation_year,
        admission.other_educational_background if admission.other_educational_background else '',
        admission.get_professional_status_display() if admission.professional_status else '',
        admission.current_occupation if admission.current_occupation else '',
        admission.current_employer if admission.current_employer else '',
        admission.get_activity_sector_display() if admission.activity_sector else '',
        admission.past_professional_activities if admission.past_professional_activities else '',
        admission.motivation if admission.motivation else '',
        admission.professional_personal_interests if admission.professional_personal_interests else '',
        admission.formation.acronym,
        _('Yes') if admission.formation.training_aid else _('No'),
        admission.get_faculty() if admission.get_faculty() else '',
        admission.formation.formation_administrators,
        admission.awareness_list
    ]


def _get_titles():
    return [
        str(_('Name')),
        str(_('First name')),
        str(_('Email')),
        str(_('State')),
        str(_('Gender')),
        str(_('Citizenship')),
        str(_('Birth date')),
        str(_('Birth location')),
        str(_('Birth country')),
        str(_('Mobile phone')),
        str(_('Contact address')),
        str(_('High school diploma')),
        str(_('High school graduation year')),
        str(_('Last degree level')),
        str(_('Last degree institution')),
        str(_('Last degree graduation year')),
        str(_('Other educational background')),
        str(_('Professional status')),
        str(_('Current occupation')),
        str(_('Current employer')),
        str(_('Activity sector')),
        str(_('Past professional activities')),
        str(_('Motivation')),
        str(_('Professional and personal interests')),
        str(_('Formation')),
        str(_('Training aid')),
        str(_('Faculty')),
        str(_('Formation administrator(s)')),
        str(_('Awareness')),
    ]
