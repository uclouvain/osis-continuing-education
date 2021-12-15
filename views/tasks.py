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
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from rules.contrib.views import permission_required

from base.views.common import display_error_messages, display_success_messages
from continuing_education.auth.roles.continuing_education_manager import is_continuing_education_manager
from continuing_education.auth.roles.continuing_education_training_manager import \
    is_continuing_education_training_manager
from continuing_education.business.admission import save_state_changed_and_send_email
from continuing_education.forms.admission import RejectedAdmissionForm, WaitingAdmissionForm, \
    ConditionAcceptanceAdmissionForm, CancelAdmissionForm
from continuing_education.models.admission import Admission, filter_authorized_admissions
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED, \
    REJECTED, WAITING, CANCELLED, CANCELLED_NO_REGISTRATION_REQUIRED
from continuing_education.views.common import save_and_create_revision, get_revision_messages, \
    REGISTRATION_FILE_RECEIVED
from continuing_education.views.home import is_continuing_education_student_worker


@login_required
@permission_required('continuing_education.view_admission', raise_exception=True)
def list_tasks(request):
    is_continuing_education_mgr = is_continuing_education_manager(request.user)
    is_continuing_education_training_mgr = is_continuing_education_training_manager(request.user)
    if not is_continuing_education_mgr and not is_continuing_education_training_mgr \
            and not is_continuing_education_student_worker(request.user):
        raise PermissionDenied
    all_admissions = Admission.objects.select_related(
        'person_information__person', 'formation__education_group'
    )
    if not is_continuing_education_student_worker(request.user):
        all_admissions = filter_authorized_admissions(request.user, all_admissions)

    registrations_to_validate = all_admissions.filter(
        state=admission_state_choices.REGISTRATION_SUBMITTED,
    ).formations()

    admissions_to_accept = all_admissions.filter(
        Q(state=admission_state_choices.SUBMITTED) | Q(state=admission_state_choices.WAITING)
    ).formations()

    admissions_diploma_to_produce = all_admissions.filter(
        diploma_produced=False,
        ucl_registration_complete=True,
        payment_complete=True,
        assessment_succeeded=True,
        state=admission_state_choices.VALIDATED
    )

    rejected_adm_form = RejectedAdmissionForm(
        request.POST or None,
        prefix='rejected',
    )

    waiting_adm_form = WaitingAdmissionForm(
        request.POST or None,
    )

    condition_acceptance_adm_form = ConditionAcceptanceAdmissionForm(
        request.POST or None,
    )

    cancel_adm_form = CancelAdmissionForm(
        request.POST or None,
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
        'condition_acceptance_adm_form': condition_acceptance_adm_form,
        'rejected_adm_form': rejected_adm_form,
        'waiting_adm_form': waiting_adm_form,
        'cancel_adm_form': cancel_adm_form,
    })


@login_required
@require_http_methods(['POST'])
@permission_required('continuing_education.mark_diploma_produced', raise_exception=True)
def mark_diplomas_produced(request):
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
def process_admissions(request):
    if not is_continuing_education_training_manager(request.user):
        raise PermissionDenied
    selected_admission_ids = request.POST.getlist("selected_admissions_to_accept", default=[])
    new_state = request.POST.get('new_state')
    if selected_admission_ids:
        _process_admissions_list(request, selected_admission_ids, new_state)
        msg = _('Successfully change of state %s admission(s).') % len(selected_admission_ids)
        display_success_messages(request, msg)
    else:
        display_error_messages(request, _('Please select at least one admission to process.'))

    return redirect(reverse("list_tasks"))


def _process_admissions_list(request, registrations_ids_list, new_status):
    admissions_list = Admission.objects.filter(id__in=registrations_ids_list)
    admissions_list_states = admissions_list.values_list('state', flat=True)
    if not all(state == admission_state_choices.SUBMITTED or admission_state_choices.WAITING
               for state in admissions_list_states):
        raise PermissionDenied(_('The admission must be submitted or waiting to be accepted.'))

    condition_exists = request.POST.get('condition_of_acceptance_existing') == 'True'
    reason_by_state = {
        ACCEPTED: request.POST.get('condition_of_acceptance') if condition_exists else '',
        ACCEPTED_NO_REGISTRATION_REQUIRED: request.POST.get('condition_of_acceptance') if condition_exists else '',
        REJECTED: request.POST.get('rejected-other_reason') or request.POST.get('rejected-rejected_reason'),
        WAITING: request.POST.get('other_reason') or request.POST.get('waiting_reason'),
        CANCELLED: request.POST.get('state_reason'),
        CANCELLED_NO_REGISTRATION_REQUIRED: request.POST.get('state_reason')
    }

    if new_status not in admission_state_choices.NEW_ADMIN_STATE.keys():
        raise PermissionDenied(_('Incorrect state'))

    for admission in admissions_list:
        _update_admission(request, admission, new_status, reason_by_state)


def _update_admission(request, admission, new_status, reason_by_state):
    admission._original_state = admission.state
    admission.state = new_status
    reason = reason_by_state.get(admission.state, '')
    if admission.state in [ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED]:
        admission.condition_of_acceptance = reason
        admission.academic_year_id = request.POST.get('academic_year')
    else:
        admission.state_reason = reason
    admission.save()
    save_state_changed_and_send_email(admission, request.user)


@require_http_methods(['POST'])
@login_required
@permission_required('continuing_education.change_received_file_state')
def paper_registrations_file_received(request):
    selected_registration_ids = request.POST.getlist("selected_registrations_to_validate", default=[])
    if selected_registration_ids:
        _update_registration_field_for_list(selected_registration_ids, "registration_file_received", request.user)
        msg = _('Successfully processed %s registration(s).') % len(selected_registration_ids)
        display_success_messages(request, msg)
    else:
        display_error_messages(request, _('Please select at least one registration to validate.'))
    return redirect(reverse("list_tasks"))


def _update_registration_field_for_list(registrations_ids_list, field_to_update, user):
    registrations_list = Admission.objects.filter(id__in=registrations_ids_list)
    registrations_list_states = registrations_list.values_list('state', flat=True)
    if not all(state == admission_state_choices.REGISTRATION_SUBMITTED for state in registrations_list_states):
        raise PermissionDenied(_('The registration must be submitted to be validated.'))

    for registration in registrations_list:
        if field_to_update == 'registration_file_received':
            registration.registration_file_received = True
            save_and_create_revision(get_revision_messages(REGISTRATION_FILE_RECEIVED), registration, user)
