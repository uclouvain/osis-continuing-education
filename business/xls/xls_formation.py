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
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from base.business.xls import get_name_or_username
from continuing_education.business.xls.xls_common import form_filters
from continuing_education.templatetags.formation import get_faculty, get_most_recent_education_group, \
    get_active_continuing_education_formation
from osis_common.document import xls_build

XLS_DESCRIPTION = _('Formations list')
XLS_FILENAME = _('Formations_list')
WORKSHEET_TITLE = _('Formations list')


def create_xls(user, formation_list, form):
    filters = form_filters(form)

    working_sheets_data = prepare_xls_content(formation_list)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: _get_titles(),
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(formation_list):
    return [extract_xls_data_from_formation(formation) for formation in formation_list]


def extract_xls_data_from_formation(formation):
    most_recent_education_grp = get_most_recent_education_group(formation)

    try:
        continuing_education_training = formation.continuingeducationtraining
    except ObjectDoesNotExist:
        continuing_education_training = None

    return [
        formation.most_recent_acronym,
        get_faculty(most_recent_education_grp),
        most_recent_education_grp.title,
        get_active_continuing_education_formation(formation),
        _('Yes') if continuing_education_training and continuing_education_training.training_aid else _('No'),
        continuing_education_training.formation_administrators if continuing_education_training else '',
    ]


def _get_titles():
    return [
        str(_('Acronym')),
        str(_('Faculty')),
        str(_('Title')),
        str(_('State')),
        str(_('Training aid')),
        str(_('Formation administrator(s)')),
    ]
