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
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.education_group import EducationGroup
from continuing_education.forms.search import FormationFilterForm
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.views.common import get_object_list
from base.views.common import display_success_messages, display_error_messages
from continuing_education.business.xls.xls_formation import create_xls


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_formations(request):
    formation_list = []

    search_form = FormationFilterForm(request.POST)
    if search_form.is_valid():
        formation_list = search_form.get_formations()

    if request.POST.get('xls_status') == "xls_formations":
        return create_xls(request.user, formation_list, search_form)

    return render(request, "formations.html", {
        'formations': get_object_list(request, formation_list),
        'search_form': search_form
    })


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def formations_activate(request):
    # Function to activate or desactivate
    selected_formations_id = request.POST.getlist("selected_action", default=[])
    new_state = _get_new_state(request)
    if new_state is not None:
        if selected_formations_id:
            _formation_activate(request, selected_formations_id, new_state)
        else:
            display_error_messages(request, _('Please select at least one formation'))

    return redirect(reverse('formation'))


def _get_new_state(request):
    new_state = request.POST.get("new_state")
    if new_state == "true":
        return True
    elif new_state == "false":
        return False
    return None


def _formation_activate(request, selected_formations_id, new_state):
    activated_count = 0
    for formation_id in selected_formations_id:

        continuing_education_training = ContinuingEducationTraining.objects.filter(
            education_group__id=formation_id).first()
        if continuing_education_training:
            if continuing_education_training.active != new_state:
                continuing_education_training.active = new_state
                continuing_education_training.save()
                activated_count += 1
        else:
            education_grp = EducationGroup.objects.get(id=formation_id)
            if education_grp:
                ContinuingEducationTraining(education_group=education_grp,
                                            active=new_state).save()
                activated_count += 1

    _set_information_message(activated_count, request, new_state)


def _set_information_message(count, request, new_state):

    if count > 0:
        _set_success_message(count, new_state, request)
    else:
        _set_error_message(new_state, request)


def _set_success_message(count, new_state, request):
    if new_state:
        success_msg = _("Formation is now active")
    else:
        success_msg = _("Formation is now inactive")
    if count > 1:
        if new_state:
            success_msg = _("Formation are now active")
        else:
            success_msg = _("Formation are now inactive")
    display_success_messages(request, success_msg)


def _set_error_message(new_state, request):
    if new_state:
        msg = _('No formation activated')
    else:
        msg = _('No formation inactivated')
    display_error_messages(request, msg)
