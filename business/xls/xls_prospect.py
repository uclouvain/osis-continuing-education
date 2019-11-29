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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.utils.translation import gettext_lazy as _

from base.business.xls import get_name_or_username
from continuing_education.models.prospect import Prospect
from osis_common.document import xls_build

XLS_DESCRIPTION = _('Prospects list')
XLS_FILENAME = _('Prospects_list')
WORKSHEET_TITLE = _('Prospects list')


def create_xls(user):
    working_sheets_data = _prepare_xls_content(Prospect.objects.all())
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: _get_titles(),
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters))


def _prepare_xls_content(prospect_list):
    return [_extract_xls_data(admission) for admission in prospect_list]


def _extract_xls_data(prospect):
    return [
        prospect.name if prospect.name else '',
        prospect.first_name if prospect.first_name else '',
        prospect.city if prospect.city else '',
        prospect.email,
        prospect.phone_number if prospect.phone_number else '',
        prospect.formation,
    ]


def _get_titles():
    return [
        str(_('Name')),
        str(_('First name')),
        str(_('City')),
        str(_('Email')),
        str(_('Phone number')),
        str(_('Formation')),
    ]
