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
from osis_common.document import xls_build
from continuing_education.business.xls.xls_common import form_filters


TITLES = [
    str(_('Name')),
    str(_('First name')),
    str(_('Email')),
    str(_('Formation')),
    str(_('Faculty')),
    str(_('Registered')),
    str(_('Paid')),
    str(_('Status')),
]
XLS_DESCRIPTION = _('Registrations list')
XLS_FILENAME = _('Registrations_list')
WORKSHEET_TITLE = _('Registrations list')


def create_xls_registration(user, registrations_list, form):
    working_sheets_data = prepare_xls_content(registrations_list)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters),
                                  form_filters(form))


def prepare_xls_content(registrations_list):
    return [extract_xls_data_from_registration(registration) for registration in registrations_list]


def extract_xls_data_from_registration(registration):
    return [
        registration.person_information.person.last_name,
        registration.person_information.person.first_name,
        registration.email,
        registration.formation_display,
        registration.get_faculty() if registration.get_faculty() else '',
        _('Yes') if registration.ucl_registration_complete else _('No'),
        _('Yes') if registration.payment_complete else _('No'),
        _(registration.state) if registration.state else ''
    ]
