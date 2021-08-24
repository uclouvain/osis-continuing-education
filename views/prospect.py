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

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from rules.contrib.views import permission_required, objectgetter

from continuing_education.business.prospect import get_prospects_by_user
from continuing_education.business.xls.xls_prospect import create_xls
from continuing_education.models.prospect import Prospect
from continuing_education.views.common import get_object_list
from osis_common.decorators.download import set_download_cookie


@login_required
@permission_required('continuing_education.view_prospect', raise_exception=True)
def list_prospects(request):
    prospects_list = get_prospects_by_user(request.user)
    return render(request, "prospects.html", {
        'prospects': get_object_list(request, prospects_list),
        'prospects_count': len(prospects_list)
    })


@login_required
@permission_required(
    'continuing_education.view_prospect',
    fn=objectgetter(Prospect, 'prospect_id'),
    raise_exception=True
)
def prospect_details(request, prospect_id):
    prospect = get_object_or_404(Prospect, pk=prospect_id)
    return render(request, "prospect_details.html", {
        'prospect': prospect
    })


@set_download_cookie
@login_required
@permission_required('continuing_education.export_prospect', raise_exception=True)
def prospect_xls(request):
    return create_xls(request.user)
