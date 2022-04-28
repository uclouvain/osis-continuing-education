##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from rules.contrib.views import permission_required, objectgetter

from base.views.common import display_error_messages, display_success_messages
from continuing_education.business.prospect import get_prospects_by_user
from continuing_education.business.xls.xls_prospect import create_xls
from continuing_education.forms.search import ProspectFilterForm
from continuing_education.models.prospect import Prospect
from continuing_education.views.common import get_object_list
from django.utils.translation import gettext_lazy as _


@login_required
@permission_required('continuing_education.view_prospect', raise_exception=True)
def list_prospects(request):
    search_form = ProspectFilterForm(data=request.GET, user=request.user)

    if search_form.is_valid():
        prospects_list = search_form.get_propects_with_filter()
    else:
        prospects_list = Prospect.objects.none()

    if request.GET.get('xls_status') == "xls_prospects":
        return prospect_xls(request, prospects_list, search_form)

    return render(request, "continuing_education/prospects.html", {
        'prospects': get_object_list(request, prospects_list),
        'prospects_count': len(prospects_list),
        'search_form': search_form
    })


@login_required
@permission_required(
    'continuing_education.view_prospect',
    fn=objectgetter(Prospect, 'prospect_id'),
    raise_exception=True
)
def prospect_details(request, prospect_id):
    prospect = get_object_or_404(Prospect, pk=prospect_id)
    return render(request, "continuing_education/prospect_details.html", {
        'prospect': prospect
    })


@login_required
@permission_required('continuing_education.export_prospect', raise_exception=True)
def prospect_xls(request, prospects_list, search_form: ProspectFilterForm):
    return create_xls(request.user, prospects_list, search_form)



@login_required
@permission_required('continuing_education.delete_prospect', raise_exception=True)
def delete_prospects(request):
    selected_prospects_id = request.POST.getlist("selected_action", default=[])
    if selected_prospects_id:
        Prospect.objects.filter(id__in=selected_prospects_id).delete()
        msg = _("Prospect(s) deleted")
        display_success_messages(request, msg)
    else:
        _set_error_message(request)
    return redirect(reverse('prospects'))


def _set_error_message(request):
    error_msg = _('Please select at least one prospect to delete')
    display_error_messages(request, error_msg)
