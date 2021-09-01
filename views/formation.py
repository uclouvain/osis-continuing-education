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
import ast

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import permission_required, objectgetter

from base.models.education_group import EducationGroup
from base.utils.cache import cache_filter
from base.views.common import display_success_messages, display_error_messages
from continuing_education.auth.roles.continuing_education_training_manager import \
    is_continuing_education_training_manager, ContinuingEducationTrainingManager
from continuing_education.business.xls.xls_formation import create_xls
from continuing_education.forms.address import AddressForm
from continuing_education.forms.formation import ContinuingEducationTrainingForm
from continuing_education.forms.search import FormationFilterForm
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.views.common import get_object_list


@login_required
@permission_required('continuing_education.view_continuingeducationtraining', raise_exception=True)
@cache_filter(exclude_params=['xls_status'])
def list_formations(request):
    formation_list = []

    search_form = FormationFilterForm(request.GET)
    if search_form.is_valid():
        formation_list = search_form.get_formations()

    if request.GET.get('xls_status') == "xls_formations":
        return create_xls(request.user, formation_list, search_form)
    continuing_education_training_manager = is_continuing_education_training_manager(request.user)
    trainings_managing = list(
        ContinuingEducationTrainingManager.objects.filter(
            person=request.user.person
        ).values_list('training', flat=True).distinct(
            'training')
    ) if continuing_education_training_manager else None
    return render(
        request, "formations.html",
        {
            'formations': get_object_list(request, formation_list),
            'formations_number': len(formation_list),
            'search_form': search_form,
            'continuing_education_training_manager': continuing_education_training_manager,
            'trainings_managing': trainings_managing
        }
    )


@login_required
@permission_required('continuing_education.change_continuingeducationtraining', raise_exception=True)
def update_formations(request):
    redirect_url = request.META.get('HTTP_REFERER', reverse('formation'))

    selected_formations_ids = request.GET.getlist("selected_action", default=[])
    if not selected_formations_ids:
        display_error_messages(request, _('Please select at least one formation'))
        return redirect(redirect_url)

    new_state = ast.literal_eval(request.GET.get("new_state"))
    new_training_aid_value = ast.literal_eval(request.GET.get("new_training_aid_value"))

    if new_state is not None:
        _formation_activate(request, selected_formations_ids, new_state)
    elif new_training_aid_value is not None:
        _update_training_aid_value(request, selected_formations_ids, new_training_aid_value)

    return redirect(redirect_url)


def _formation_activate(request, selected_formations_ids, new_state):
    activated_count = 0
    for formation_id in selected_formations_ids:
        continuing_education_training = ContinuingEducationTraining.objects.filter(
            education_group__id=formation_id).first()
        if continuing_education_training:
            activated_count = _edit_continuing_education_training(activated_count,
                                                                  continuing_education_training,
                                                                  new_state)
        else:
            education_grp = EducationGroup.objects.get(id=formation_id)
            if education_grp:
                ContinuingEducationTraining(education_group=education_grp,
                                            active=new_state).save()
                activated_count += 1

    _set_information_message(activated_count, request, new_state)


def _edit_continuing_education_training(activated_count, continuing_education_training, new_state):
    if continuing_education_training.active != new_state:
        continuing_education_training.active = new_state
        continuing_education_training.save()
        activated_count += 1
    return activated_count


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


def _update_training_aid_value(request, selected_formations_ids, new_training_aid_value):
    for formation_id in selected_formations_ids:
        education_grp = get_object_or_404(EducationGroup, id=formation_id)
        ContinuingEducationTraining.objects.update_or_create(
            education_group=education_grp,
            defaults={'training_aid': new_training_aid_value, 'education_group': education_grp},
        )
    success_msg = _('Successfully defined training aid to %(new_value)s for %(quantity_updated)s trainings.') % {
        "new_value": _('Yes') if new_training_aid_value else _('No'),
        "quantity_updated": len(selected_formations_ids)
    }
    display_success_messages(request, success_msg)


@login_required
@permission_required('continuing_education.view_continuingeducationtraining', raise_exception=True)
def formation_detail(request, formation_id):
    formation = ContinuingEducationTraining.objects.filter(
        education_group__id=formation_id).first()
    if formation:
        can_edit_formation = request.user.has_perm(
            'continuing_education.change_continuingeducationtraining', obj=formation
        )
        return render(
            request, "formation_detail.html",
            {
                'formation': formation,
                'can_edit_formation': can_edit_formation,
            }
        )
    else:
        raise Http404()


@login_required
@permission_required(
    'continuing_education.change_continuingeducationtraining',
    fn=objectgetter(ContinuingEducationTraining, 'formation_id'),
    raise_exception=True
)
def formation_edit(request, formation_id):
    formation = get_object_or_404(
        ContinuingEducationTraining.objects.select_related('postal_address', 'education_group'),
        pk=formation_id
    )
    form = ContinuingEducationTrainingForm(request.POST or None, user=request.user, instance=formation)
    address_form = AddressForm(request.POST or None, instance=formation.postal_address)
    if all([form.is_valid(), address_form.is_valid()]):
        address = address_form.save()
        formation = form.save(commit=False)
        formation.postal_address = address
        formation.save()
        return redirect(reverse('formation_detail', kwargs={'formation_id': formation.education_group.id}))
    return render(
        request,
        "formation_form.html",
        {
            'formation': formation,
            'form': form,
            'address_form': address_form
        }
    )
