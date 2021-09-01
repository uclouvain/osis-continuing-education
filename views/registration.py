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
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import permission_required

from base.utils.cache import cache_filter
from base.views.common import display_error_messages, display_success_messages
from continuing_education.business.xls.xls_registration import create_xls_registration
from continuing_education.forms.address import AddressForm
from continuing_education.forms.registration import RegistrationForm
from continuing_education.forms.search import RegistrationFilterForm
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission, filter_authorized_admissions, can_access_admission, \
    admission_getter
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.views.common import get_object_list, save_and_create_revision, \
    get_appropriate_revision_message
from continuing_education.views.home import is_continuing_education_student_worker


@login_required
@permission_required('continuing_education.view_admission', raise_exception=True)
@cache_filter(exclude_params=['xls_status'])
def list_registrations(request):
    search_form = RegistrationFilterForm(request.GET, user=request.user)
    user_is_continuing_education_student_worker = is_continuing_education_student_worker(request.user)
    admission_list = Admission.registration_objects.all()
    if search_form.is_valid():
        admission_list = search_form.get_registrations()

    if not user_is_continuing_education_student_worker:
        admission_list = filter_authorized_admissions(request.user, admission_list)

    if request.GET.get('xls_status') == "xls_registrations":
        return export_registrations(request, admission_list, search_form)

    return render(request, "registrations.html", {
        'admissions': get_object_list(request, admission_list),
        'admissions_number': len(admission_list),
        'search_form': search_form,
        'user_is_continuing_education_student_worker': user_is_continuing_education_student_worker,
        'ucl_registration_state_choices': UCLRegistrationState.__members__
    })


@login_required
@permission_required('continuing_education.export_admission')
def export_registrations(request, admission_list, search_form):
    if request.GET.get('xls_status') == "xls_registrations":
        return create_xls_registration(request.user, admission_list, search_form)


@login_required
@permission_required('continuing_education.change_admission', fn=admission_getter, raise_exception=True)
def registration_edit(request, admission_id):
    admission = get_object_or_404(
        Admission.objects.select_related(
            'billing_address',
            'residence_address',
            'address'
        ),
        pk=admission_id
    )
    can_access_admission(request.user, admission)

    if admission.is_draft():
        raise PermissionDenied

    address = admission.address
    billing_address = admission.billing_address
    residence_address = admission.residence_address
    registration_form = RegistrationForm(request.POST or None, instance=admission, user=request.user)
    billing_address_form = AddressForm(request.POST or None, instance=admission.billing_address, prefix="billing")
    residence_address_form = AddressForm(request.POST or None, instance=admission.residence_address, prefix="residence")

    errors = []
    if registration_form.is_valid() and billing_address_form.is_valid() and residence_address_form.is_valid():
        billing_address = _update_or_create_specific_address(
            admission.address,
            billing_address,
            billing_address_form,
            not registration_form.cleaned_data['use_address_for_billing']
        )
        residence_address = _update_or_create_specific_address(
            admission.address,
            residence_address,
            residence_address_form,
            not registration_form.cleaned_data['use_address_for_post']
        )
        admission = registration_form.save(commit=False)
        admission.address = address
        admission.billing_address = billing_address
        admission.residence_address = residence_address
        message = get_appropriate_revision_message(registration_form)
        save_and_create_revision(message, admission, request.user)

        return redirect(reverse('admission_detail', kwargs={'admission_id': admission_id}) + "#registration")
    else:
        errors.append(registration_form.errors)

    return render(
        request,
        'registration_form.html',
        {
            'admission': admission,
            'registration_form': registration_form,
            'billing_address_form': billing_address_form,
            'residence_address_form': residence_address_form,
            'errors': errors,
        }
    )


def _update_or_create_specific_address(admission_address, specific_address, specific_address_form, use_address):
    if use_address:
        return admission_address
    elif specific_address == admission_address:
        # We must create a new specific address, not update the admission's address.
        specific_address = Address.objects.create(**specific_address_form.cleaned_data)
        return specific_address
    else:
        specific_address = specific_address_form.save()
        return specific_address


@login_required
@permission_required('continuing_education.change_received_file_state', raise_exception=True)
def receive_files_procedure(request):
    selected_admissions_id = request.POST.getlist("selected_action", default=[])
    redirection = request.META.get('HTTP_REFERER')
    if selected_admissions_id:
        _mark_folders_as_received(request, selected_admissions_id, True)
        return redirect(reverse('registration'))
    else:
        _set_error_message(request)
        return HttpResponseRedirect(redirection)


def _mark_folders_as_received(request, selected_admissions_ids, new_received_file_state):
    Admission.objects.filter(pk__in=selected_admissions_ids).update(registration_file_received=new_received_file_state)
    _set_success_message(request, len(selected_admissions_ids) > 1, new_received_file_state)


def _set_received_file_status(registration, received_file_state):
    if registration:
        registration.registration_file_received = received_file_state
        registration.save()


def _set_success_message(request, is_plural, received_file_state=True):
    success_msg = "{} {}".format(
        _('Files are now mark as ') if is_plural else _('File is now mark as '),
        _('received') if received_file_state else _('not received')
    )
    display_success_messages(request, success_msg)


@login_required
@permission_required('continuing_education.change_received_file_state', raise_exception=True)
def receive_file_procedure(request, admission_id):
    redirection = request.META.get('HTTP_REFERER')
    admission = _switch_received_file_state(admission_id)
    _set_success_message(request, False, admission.registration_file_received)
    return HttpResponseRedirect(redirection)


def _set_error_message(request):
    error_msg = _('Please select at least one file to mark as received')
    display_error_messages(request, error_msg)


def _switch_received_file_state(admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    _set_received_file_status(admission, not admission.registration_file_received)
    return admission


@login_required
@permission_required('continuing_education.cancel_admission', raise_exception=True)
def list_cancelled(request):
    admission_list = Admission.objects.filter(state__in=[
        admission_state_choices.CANCELLED,
        admission_state_choices.CANCELLED_NO_REGISTRATION_REQUIRED
    ])
    admission_list = filter_authorized_admissions(request.user, admission_list)

    return render(request, "cancellations.html", {
        'admissions': get_object_list(request, admission_list)
    })
