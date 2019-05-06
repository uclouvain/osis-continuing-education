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
import itertools
from collections import OrderedDict

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from base.utils.cache import cache_filter
from base.views.common import display_success_messages, display_error_messages
from continuing_education.business.admission import send_invoice_uploaded_email, send_state_changed_email, \
    check_required_field_for_participant
from continuing_education.business.xls.xls_admission import create_xls
from continuing_education.forms.account import ContinuingEducationPersonForm
from continuing_education.forms.address import AddressForm, ADDRESS_PARTICIPANT_REQUIRED_FIELDS
from continuing_education.forms.admission import AdmissionForm, RejectedAdmissionForm, WaitingAdmissionForm, \
    ADMISSION_PARTICIPANT_REQUIRED_FIELDS, ConditionAcceptanceAdmissionForm
from continuing_education.forms.person import PersonForm
from continuing_education.forms.search import AdmissionFilterForm
from continuing_education.models import continuing_education_person
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission, filter_authorized_admissions, can_access_admission
from continuing_education.models.enums import admission_state_choices, file_category_choices
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, VALIDATED, \
    REGISTRATION_SUBMITTED, ACCEPTED
from continuing_education.models.file import AdmissionFile
from continuing_education.views.common import display_errors
from continuing_education.views.common import get_object_list
from continuing_education.views.file import _get_file_category_choices_with_disabled_parameter, _upload_file
from osis_common.decorators.ajax import ajax_required
from continuing_education.business.perms import is_not_student_worker
from continuing_education.views.home import is_continuing_education_student_worker


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
@user_passes_test(is_not_student_worker)
@cache_filter(exclude_params=['xls_status'])
def list_admissions(request):
    search_form = AdmissionFilterForm(request.GET)
    admission_list = []
    if search_form.is_valid():
        admission_list = search_form.get_admissions()

    admission_list = filter_authorized_admissions(request.user, admission_list)

    if request.GET.get('xls_status') == "xls_admissions":
        return create_xls(request.user, admission_list, search_form)

    return render(request, "admissions.html", {
        'admissions': get_object_list(request, admission_list),
        'admissions_number': len(admission_list),
        'search_form': search_form,
    })


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def admission_detail(request, admission_id):
    user_is_continuing_education_student_worker = is_continuing_education_student_worker(request.user)

    if not user_is_continuing_education_student_worker:
        can_access_admission(request.user, admission_id)

    admission = get_object_or_404(Admission, pk=admission_id)
    files = AdmissionFile.objects.all().filter(admission=admission_id)
    accepted_states = admission_state_choices.NEW_ADMIN_STATE[admission.state]
    states = _get_states_choices(accepted_states, admission, request)

    adm_form = AdmissionForm(
        request.POST or None,
        instance=admission,
    )

    if request.method == 'POST' and request.FILES:
        return _upload_file(request, admission)

    rejected_adm_form = RejectedAdmissionForm(
        request.POST or None,
        instance=admission,
        prefix='rejected',
        )

    waiting_adm_form = WaitingAdmissionForm(
        request.POST or None,
        instance=admission,
        )

    condition_acceptance_adm_form = ConditionAcceptanceAdmissionForm(
        request.POST or None,
        instance=admission,
        )

    if adm_form.is_valid():
        forms = (adm_form, waiting_adm_form, rejected_adm_form, condition_acceptance_adm_form)
        return _change_state(request, forms, accepted_states, admission)

    return render(
        request, "admission_detail.html",
        {
            'admission': admission,
            'files': files,
            'states': states,
            'admission_form': adm_form,
            'rejected_adm_form': rejected_adm_form,
            'waiting_adm_form': waiting_adm_form,
            'file_categories_choices': _get_file_category_choices_with_disabled_parameter(admission),
            'invoice': file_category_choices.INVOICE,
            'condition_acceptance_adm_form': condition_acceptance_adm_form,
            'user_is_continuing_education_student_worker': user_is_continuing_education_student_worker,
        }
    )


def _change_state(request, forms, accepted_states, admission):
    adm_form, waiting_adm_form, rejected_adm_form, condition_acceptance_adm_form = forms
    new_state = adm_form.cleaned_data['state']
    if new_state in accepted_states.get('states', []):
        return _new_state_management(request, forms, admission, new_state)


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
@user_passes_test(is_not_student_worker)
def send_invoice_notification_mail(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    if _invoice_file_exists_for_admission(admission):
        send_invoice_uploaded_email(admission)
        display_success_messages(request, _("A notification email has been sent to the participant"))
    else:
        display_error_messages(request, _("There is no invoice for this admission, notification email not sent"))

    return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}) + '#documents')


def _invoice_file_exists_for_admission(admission):
    return AdmissionFile.objects.filter(admission=admission, file_category=file_category_choices.INVOICE).exists()


@login_required
@permission_required('continuing_education.change_admission', raise_exception=True)
@user_passes_test(is_not_student_worker)
def admission_form(request, admission_id=None):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    if admission:
        can_access_admission(request.user, admission_id)
        if admission.is_draft():
            raise PermissionDenied
    states = admission_state_choices.NEW_ADMIN_STATE[admission.state].get('choices', ()) if admission else None
    base_person = admission.person_information.person if admission else None
    base_person_form = PersonForm(request.POST or None, instance=base_person)
    person_information = continuing_education_person.find_by_person(person=base_person)
    # TODO :: get last admission address if it exists instead of None
    address = admission.address if admission else None
    state = admission.state if admission else SUBMITTED
    adm_form = AdmissionForm(
        data=request.POST or None,
        user=request.user,
        instance=admission,
        initial={
            'state': state
        }
    )
    person_form = ContinuingEducationPersonForm(request.POST or None, instance=person_information)
    address_form = AddressForm(request.POST or None, instance=address)
    state = admission.state if admission else None
    if adm_form.is_valid() and person_form.is_valid() and address_form.is_valid():
        if address:
            address = address_form.save()
        else:
            address = Address(**address_form.cleaned_data)
            address.save()

        person = request.POST.get('person_information', None)
        if not person:
            person = person_form.save(commit=False)
            if not base_person:
                base_person = base_person_form.save()
            person.person_id = base_person.pk
            person.save()

        admission = adm_form.save(commit=False)
        admission.address = address
        admission.billing_address = address
        admission.residence_address = address
        if not admission.person_information:
            admission.person_information = person
        admission.save()
        if admission.state == DRAFT:
            return redirect(reverse('admission'))
        return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}))

    else:
        errors = list(itertools.product(adm_form.errors, person_form.errors, address_form.errors))
        display_errors(request, errors)

    return render(
        request,
        'admission_form.html',
        {
            'admission': admission,
            'admission_form': adm_form,
            'person_form': person_form,
            'address_form': address_form,
            'base_person_form': base_person_form,
            'state': state,
            'states': states
        }
    )


def _new_state_management(request, forms, admission, new_state):
    admission._original_state = admission.state
    adm_form, waiting_adm_form, rejected_adm_form, condition_acceptance_adm_form = forms
    _save_form_with_provided_reason(waiting_adm_form, rejected_adm_form, new_state, condition_acceptance_adm_form)
    if new_state != VALIDATED:
        adm_form.save()
    else:
        _validate_admission(request, adm_form)
    send_state_changed_email(adm_form.instance, request.user)
    return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}))


def _save_form_with_provided_reason(waiting_adm_form, rejected_adm_form, new_state, condition_acceptance_adm_form):
    if new_state == REJECTED and rejected_adm_form.is_valid():
            rejected_adm_form.save()
    elif new_state == WAITING and waiting_adm_form.is_valid():
            waiting_adm_form.save()
    elif new_state == ACCEPTED and condition_acceptance_adm_form.is_valid():
            condition_acceptance_adm_form.save()


def _validate_admission(request, adm_form):
    if request.user.has_perm("continuing_education.can_validate_registration"):
        adm_form.save()
    else:
        display_error_messages(
            request,
            _("Continuing education managers only are allowed to validate a registration")
        )


@ajax_required
@login_required
@permission_required("continuing_education.change_admission", raise_exception=True)
@user_passes_test(is_not_student_worker)
def validate_field(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    response = {}
    response.update(check_required_field_for_participant(admission.address,
                                                         Address._meta,
                                                         ADDRESS_PARTICIPANT_REQUIRED_FIELDS,
                                                         _('Contact address')))
    response.update(check_required_field_for_participant(admission.billing_address,
                                                         Address._meta,
                                                         ADDRESS_PARTICIPANT_REQUIRED_FIELDS,
                                                         _('Billing address')))
    response.update(check_required_field_for_participant(admission.residence_address,
                                                         Address._meta,
                                                         ADDRESS_PARTICIPANT_REQUIRED_FIELDS,
                                                         _('Residence address')))

    response.update(check_required_field_for_participant(admission,
                                                         Admission._meta,
                                                         ADMISSION_PARTICIPANT_REQUIRED_FIELDS))

    return JsonResponse(OrderedDict(sorted(response.items(), key=lambda x: x[1])), safe=False)


def _get_states_choices(accepted_states, admission, request):
    if not request.user.has_perm('continuing_education.can_validate_registration') \
            and admission.state in [REGISTRATION_SUBMITTED, VALIDATED]:
        return []
    else:
        return [] if admission and admission.is_draft() else accepted_states.get('choices', ())
