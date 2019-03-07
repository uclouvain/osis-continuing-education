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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render

from base.models.academic_year import current_academic_year
from continuing_education.forms.search import FormationFilterForm
from continuing_education.views.common import get_object_list


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_formations(request):
    formation_list = []

    search_form = FormationFilterForm(request.POST)
    if search_form.is_valid():
        formation_list = search_form.get_formations()

    return render(request, "formations.html", {
        'formations': get_object_list(request, formation_list),
        'search_form': search_form
    })


def _get_academic_year():
    curr_academic_year = current_academic_year()
    next_academic_year = curr_academic_year.next() if curr_academic_year else None
    return next_academic_year
