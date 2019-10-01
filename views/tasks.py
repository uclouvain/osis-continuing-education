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
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from base.views.common import display_error_messages, display_success_messages
from continuing_education.business.perms import is_not_student_worker, is_student_worker, registration_process
from continuing_education.models.admission import Admission, filter_authorized_admissions, \
    is_continuing_education_manager, is_continuing_education_training_manager
from continuing_education.models.enums import admission_state_choices
from continuing_education.views.common import save_and_create_revision, ADMISSION_ACCEPTED, get_revision_messages
from continuing_education.views.home import is_continuing_education_student_worker


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_tasks(request):
    is_continuing_education_mgr = is_continuing_education_manager(request.user)
    is_continuing_education_training_mgr = is_continuing_education_training_manager(request.user)
    if not is_continuing_education_mgr and not is_continuing_education_training_mgr \
            and not is_student_worker(request.user):
        raise PermissionDenied
    all_admissions = Admission.objects.select_related(
        'person_information__person', 'formation__education_group'
    ).order_by(
        'person_information__person__last_name', 'person_information__person__first_name'
    )
    if not is_student_worker(request.user):
        all_admissions = filter_authorized_admissions(request.user, all_admissions)

    registrations_to_validate = all_admissions.filter(
        state=admission_state_choices.REGISTRATION_SUBMITTED,
    ).filter(Q(registration_file_received=False) | Q(ucl_registration_complete=False))

    admissions_to_accept = all_admissions.filter(
        state=admission_state_choices.SUBMITTED
    )

    admissions_diploma_to_produce = all_admissions.filter(
        state=admission_state_choices.VALIDATED,
        diploma_produced=False
    )
    return render(request, "tasks.html", {
        'registrations_to_validate': registrations_to_validate,
        'to_validate_count': registrations_to_validate.count(),
        'admissions_diploma_to_produce': admissions_diploma_to_produce,
        'diplomas_count': admissions_diploma_to_produce.count(),
        'admissions_to_accept': admissions_to_accept,
        'continuing_education_manager': is_continuing_education_mgr,
        'continuing_education_training_manager': is_continuing_education_training_mgr,
        'user_is_continuing_education_student_worker': is_continuing_education_student_worker(request.user),
    })


@login_required
@require_http_methods(['POST'])
@permission_required('continuing_education.change_admission', raise_exception=True)
@user_passes_test(is_not_student_worker)
def mark_diplomas_produced(request):
    if not is_continuing_education_manager(request.user):
        raise PermissionDenied
    selected_registration_ids = request.POST.getlist("selected_diplomas_to_produce", default=[])
    if selected_registration_ids:
        _mark_diplomas_produced_list(selected_registration_ids)
        msg = _('Successfully marked diploma as produced for %s registrations.') % len(selected_registration_ids)
        display_success_messages(request, msg)
    else:
        display_error_messages(request, _('Please select at least one registration.'))
    return redirect(reverse("list_tasks") + '#diploma_to_produce')


def _mark_diplomas_produced_list(registrations_ids_list):
    registrations_list = Admission.objects.filter(id__in=registrations_ids_list)

    registrations_list_states = registrations_list.values_list('state', flat=True)
    if not all(state == admission_state_choices.VALIDATED for state in registrations_list_states):
        raise PermissionDenied(_('The registrations must be validated to mark diploma as produced.'))

    registrations_list.update(diploma_produced=True)


@login_required
@require_http_methods(['POST'])
@permission_required('continuing_education.change_admission', raise_exception=True)
@user_passes_test(is_not_student_worker)
def accept_admissions(request):
    if not is_continuing_education_training_manager(request.user):
        raise PermissionDenied
    selected_admission_ids = request.POST.getlist("selected_admissions_to_accept", default=[])
    if selected_admission_ids:
        _accept_admissions_list(request, selected_admission_ids)
        msg = _('Successfully accept %s admissions.') % len(selected_admission_ids)
        display_success_messages(request, msg)
    else:
        display_error_messages(request, _('Please select at least one admission to accept.'))

    return redirect(reverse("list_tasks"))


def _accept_admissions_list(request, registrations_ids_list):
    admissions_list = Admission.objects.filter(id__in=registrations_ids_list)

    admissions_list_states = admissions_list.values_list('state', flat=True)
    if not all(state == admission_state_choices.SUBMITTED for state in admissions_list_states):
        raise PermissionDenied(_('The admission must be submitted to be accepted.'))

    admissions_list.update(state=admission_state_choices.ACCEPTED, condition_of_acceptance='')
    for admission in admissions_list:
        save_and_create_revision(request.user, get_revision_messages(ADMISSION_ACCEPTED), admission)


@require_http_methods(['POST'])
@login_required
@user_passes_test(registration_process)
def paper_registrations_file_received(request):
    return _update_registrations("registration_file_received", request)


@require_http_methods(['POST'])
@login_required
@user_passes_test(registration_process)
def registrations_fulfilled(request):
    return _update_registrations("ucl_registration_complete", request)


def _update_registrations(field_to_update, request):
    selected_registration_ids = request.POST.getlist("selected_registrations_to_validate", default=[])
    if selected_registration_ids:
        _update_registration_field_for_list(selected_registration_ids, field_to_update)
        msg = _('Successfully processed %s registrations.') % len(selected_registration_ids)
        display_success_messages(request, msg)
    else:
        display_error_messages(request, _('Please select at least one registration to validate.'))
    return redirect(reverse("list_tasks"))


def _update_registration_field_for_list(registrations_ids_list, field_to_update):
    registrations_list = Admission.objects.filter(id__in=registrations_ids_list)
    registrations_list_states = registrations_list.values_list('state', flat=True)
    if not all(state == admission_state_choices.REGISTRATION_SUBMITTED for state in registrations_list_states):
        raise PermissionDenied(_('The registration must be submitted to be validated.'))

    if field_to_update == 'registration_file_received':
        registrations_list.update(registration_file_received=True)
    if field_to_update == 'ucl_registration_complete':
        registrations_list.update(ucl_registration_complete=True)
