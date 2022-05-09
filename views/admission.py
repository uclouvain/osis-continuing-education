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
import itertools
from collections import OrderedDict

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET
from rules.contrib.views import permission_required

from backoffice.settings.base import MAX_UPLOAD_SIZE
from base.utils.cache import cache_filter
from base.views.common import display_success_messages, display_error_messages, display_info_messages, \
    display_warning_messages
from continuing_education.business.admission import send_invoice_uploaded_email, save_state_changed_and_send_email, \
    check_required_field_for_participant
from continuing_education.business.registration_queue import send_admission_to_queue
from continuing_education.business.xls.xls_admission import create_xls
from continuing_education.forms.account import ContinuingEducationPersonForm
from continuing_education.forms.address import AddressForm, ADDRESS_PARTICIPANT_REQUIRED_FIELDS
from continuing_education.forms.admission import AdmissionForm, RejectedAdmissionForm, WaitingAdmissionForm, \
    ADMISSION_PARTICIPANT_REQUIRED_FIELDS, ConditionAcceptanceAdmissionForm, CancelAdmissionForm, \
    AdmissionChangeStateForm
from continuing_education.forms.person import PersonForm
from continuing_education.forms.registration import RegistrationForm
from continuing_education.forms.search import AdmissionFilterForm
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission, filter_authorized_admissions, can_access_admission, \
    admission_getter
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.enums import admission_state_choices, file_category_choices
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, VALIDATED, \
    ACCEPTED, CANCELLED, ACCEPTED_NO_REGISTRATION_REQUIRED, CANCELLED_NO_REGISTRATION_REQUIRED
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.models.file import AdmissionFile
from continuing_education.views.common import display_errors, save_and_create_revision, get_versions, \
    ADMISSION_CREATION, get_revision_messages
from continuing_education.views.common import get_object_list
from continuing_education.views.file import _get_file_category_choices_with_disabled_parameter, _upload_file
from continuing_education.views.home import is_continuing_education_student_worker
from continuing_education.views.registration import _update_or_create_specific_address
from osis_common.decorators.ajax import ajax_required


@login_required
@permission_required('continuing_education.export_admission', raise_exception=True)
@cache_filter(exclude_params=['xls_status'])
def list_admissions(request):
    search_form = AdmissionFilterForm(request.GET)

    if search_form.is_valid():
        admission_list = search_form.get_admissions()
        admission_list = filter_authorized_admissions(request.user, admission_list)
    else:
        admission_list = Admission.objects.none()

    if request.GET.get('xls_status') == "xls_admissions":
        return export_admissions(request, admission_list, search_form)

    return render(request, "admissions.html", {
        'admissions': get_object_list(request, admission_list),
        'admissions_number': admission_list.count(),
        'search_form': search_form,
    })


@login_required
@permission_required('continuing_education.export_admission')
def export_admissions(request, admission_list, search_form):
    return create_xls(request.user, admission_list, search_form)


@login_required
@permission_required('continuing_education.view_admission', fn=admission_getter, raise_exception=True)
def admission_detail(request, admission_id):
    user_is_continuing_education_student_worker = is_continuing_education_student_worker(request.user)
    admission = get_object_or_404(
        Admission.objects.formations().select_related(
            'billing_address__country',
            'address__country',
            'person_information__person',
            'person_information__birth_country',
            'citizenship',
            'formation__education_group',
        ).prefetch_related(
            'formation__managers',
            'formation__education_group__educationgroupyear_set__educationgroupversion_set',
        ),
        pk=admission_id
    )
    if not user_is_continuing_education_student_worker:
        can_access_admission(request.user, admission)

    files = AdmissionFile.objects.filter(admission=admission_id)
    accepted_states = admission_state_choices.NEW_ADMIN_STATE[admission.state]
    states = _get_states_choices(accepted_states, admission, request)

    adm_form = AdmissionChangeStateForm(
        request.POST or None,
        instance=admission,
    )

    version_list = get_versions(admission)

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

    cancel_adm_form = CancelAdmissionForm(
        request.POST or None,
        instance=admission,
    )

    admission._original_state = admission.state

    if adm_form.is_valid():
        forms = (adm_form, waiting_adm_form, rejected_adm_form, condition_acceptance_adm_form, cancel_adm_form)
        return _change_state(request, forms, accepted_states, admission)

    if adm_form.errors:
        display_error_messages(request, _('Some errors in form prevents state from being changed:'))
        display_error_messages(request, adm_form.errors)
        admission.state = admission._original_state
        return redirect(request.META['HTTP_REFERER'])

    _display_adapted_ucl_registration_message(admission, request)

    return render(
        request, "admission_detail.html",
        {
            'admission': admission,
            'files': files,
            'states': states,
            'admission_form': adm_form,
            'rejected_adm_form': rejected_adm_form,
            'waiting_adm_form': waiting_adm_form,
            'cancel_adm_form': cancel_adm_form,
            'file_categories_choices': _get_file_category_choices_with_disabled_parameter(admission),
            'invoice': file_category_choices.INVOICE,
            'condition_acceptance_adm_form': condition_acceptance_adm_form,
            'user_is_continuing_education_student_worker': user_is_continuing_education_student_worker,
            'version': version_list,
            'MAX_UPLOAD_SIZE': MAX_UPLOAD_SIZE,
            'opened_tab': request.GET.get('opened_tab'),
            'injection_not_rejected': admission.ucl_registration_complete != UCLRegistrationState.REJECTED.name
        }
    )


def _display_adapted_ucl_registration_message(admission, request):
    if admission.ucl_registration_complete == UCLRegistrationState.SENDED.name:
        display_warning_messages(request, _('Folder sended to EPC : waiting for response'))
    elif admission.ucl_registration_complete == UCLRegistrationState.REJECTED.name:
        display_error_messages(
            request,
            mark_safe(_('Folder injection into EPC failed : %(reasons)s') % {
                'reasons': admission.get_ucl_registration_error_display()
            })
        )
    elif admission.ucl_registration_complete == UCLRegistrationState.DEMANDE.name:
        display_info_messages(request, _('Folder injection into EPC succeeded : UCLouvain registration on demand'))
    elif admission.ucl_registration_complete == UCLRegistrationState.INSCRIT.name:
        display_success_messages(request, _('Folder injection into EPC succeeded : UCLouvain registration completed'))
    elif admission.ucl_registration_complete != UCLRegistrationState.INIT_STATE.name:
        display_info_messages(
            request,
            _('Folder injection into EPC succeeded : UCLouvain registration status : %(status)s') % {
                'status': admission.get_ucl_registration_complete_display()
            }
        )


def _change_state(request, forms, accepted_states, admission):
    adm_form, waiting_adm_form, rejected_adm_form, condition_acceptance_adm_form, cancel_adm_form = forms
    new_state = adm_form.instance.state
    if new_state == ACCEPTED and not admission.formation.registration_required:
        new_state = ACCEPTED_NO_REGISTRATION_REQUIRED
    if new_state == CANCELLED and not admission.formation.registration_required:
        new_state = CANCELLED_NO_REGISTRATION_REQUIRED
    if new_state in accepted_states.get('states', []):
        _save_form_with_provided_reason(
            waiting_adm_form, rejected_adm_form, new_state, condition_acceptance_adm_form, cancel_adm_form
        )
        adm_form.instance.state = new_state
        return _new_state_management(request, adm_form, admission, new_state)


@login_required
@permission_required('continuing_education.send_notification', raise_exception=True)
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
@permission_required('continuing_education.change_admission', fn=admission_getter, raise_exception=True)
def admission_form(request, admission_id=None):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    if admission:
        can_access_admission(request.user, admission)
        if admission.is_draft():
            raise PermissionDenied
    selected_person = bool(request.POST.get('person_information', False))
    states = admission_state_choices.NEW_ADMIN_STATE[admission.state].get('choices', ()) if admission else None
    base_person = admission.person_information.person if admission else None
    base_person_form = PersonForm(
        data=request.POST or None,
        instance=base_person,
        selected_person=selected_person,
        no_first_name_checked=request.POST.get('no_first_name', False)
    )
    if base_person:
        base_person_form.fields.pop('email')
    help_msg_first_letter_uppercase = _("Only the first letter uppercase.")
    base_person_form.fields['first_name'].help_text = help_msg_first_letter_uppercase
    base_person_form.fields['last_name'].help_text = help_msg_first_letter_uppercase
    person_information = ContinuingEducationPerson.objects.filter(person=base_person).first()
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
    person_form = ContinuingEducationPersonForm(
        data=request.POST or None,
        instance=person_information,
        selected_person=selected_person
    )
    address_form = AddressForm(request.POST or None, instance=address)
    state = admission.state if admission else None
    if adm_form.is_valid() and person_form.is_valid() and address_form.is_valid() and base_person_form.is_valid():
        if address:
            address = address_form.save()
        else:
            address = Address(**address_form.cleaned_data)
            address.save()

        person_must_be_saved = not selected_person or admission_id
        if person_must_be_saved:
            person = person_form.save(commit=False)
            base_person = base_person_form.save()
            person.person_id = base_person.pk
            person.save()

        admission = adm_form.save(commit=False)
        admission.address = address
        admission.billing_address = address
        admission.residence_address = address
        if not admission.person_information:
            admission.person_information = person
        if admission_id:
            admission.save()
        else:
            save_and_create_revision(get_revision_messages(ADMISSION_CREATION), admission, request.user)
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
            'states': states,
            'selected_person': selected_person,
        }
    )


def _new_state_management(request, adm_form, admission, new_state):
    if new_state != VALIDATED:
        save_state_changed_and_send_email(adm_form.instance, request.user)
    else:
        _validate_admission(request, admission, adm_form)
    query_param = ('?opened_tab=' + request.POST.get('opened_tab')) if request.POST.get('opened_tab') else ''
    return redirect(
        reverse('admission_detail', kwargs={'admission_id': admission.pk}) + query_param
    )


def _save_form_with_provided_reason(waiting_adm_form, rejected_adm_form, new_state, condition_acceptance_adm_form,
                                    cancel_adm_form):
    if new_state == REJECTED and rejected_adm_form.is_valid():
        rejected_adm_form.save()
    elif new_state == WAITING and waiting_adm_form.is_valid():
        waiting_adm_form.save()
    elif new_state in [ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED] and condition_acceptance_adm_form.is_valid():
        condition_acceptance_adm_form.save()
    elif new_state in [CANCELLED, CANCELLED_NO_REGISTRATION_REQUIRED] and cancel_adm_form.is_valid():
        cancel_adm_form.save()


def _validate_admission(request, admission, adm_form):
    if request.user.has_perm("continuing_education.validate_registration", adm_form.instance):
        save_state_changed_and_send_email(adm_form.instance, request.user)
        send_admission_to_queue(request, admission)
    else:
        display_error_messages(
            request,
            _("Continuing education managers and student workers only are allowed to validate a registration")
        )


@ajax_required
@login_required
@permission_required("continuing_education.change_admission", fn=admission_getter, raise_exception=True)
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
    can_change_state = request.user.has_perm('continuing_education.change_admission_state', admission)
    cannot_validate_registration = not request.user.has_perm('continuing_education.validate_registration', admission)
    admission_is_draft = admission and admission.is_draft()
    registration_is_submitted = admission.is_registration_submitted()
    registration_is_validated = admission.is_validated()

    if can_change_state:
        if admission_is_draft:
            return []
        elif cannot_validate_registration and (registration_is_submitted or registration_is_validated):
            return []
        else:
            return accepted_states.get('choices', ())

    return []


@ajax_required
@login_required
@require_GET
def get_formation_information(request):
    formation_id = request.GET.get('formation_id', None)
    training = ContinuingEducationTraining.objects.get(pk=formation_id)
    return JsonResponse(data={'additional_information_label': training.additional_information_label})


@login_required
@permission_required('continuing_education.change_admission', fn=admission_getter, raise_exception=True)
def billing_edit(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    can_access_admission(request.user, admission)

    if admission.is_draft() or admission.formation.registration_required:
        raise PermissionDenied

    registration_form = RegistrationForm(request.POST or None, instance=admission, only_billing=True, user=request.user)
    address = admission.address
    billing_address = admission.billing_address
    billing_address_form = AddressForm(request.POST or None, instance=admission.billing_address, prefix="billing")

    errors = []
    if registration_form.is_valid() and billing_address_form.is_valid():
        billing_address = _update_or_create_specific_address(
            address,
            billing_address,
            billing_address_form,
            not registration_form.cleaned_data['use_address_for_billing']
        )

        admission = registration_form.save(commit=False)
        admission.billing_address = billing_address
        admission.save()

        return redirect(reverse('admission_detail', kwargs={'admission_id': admission_id}) + "#billing")
    else:
        errors.append(billing_address_form.errors.update(registration_form.errors))

    return render(
        request,
        'admission_billing_form.html',
        {
            'admission': admission,
            'registration_form': registration_form,
            'billing_address_form': billing_address_form,
            'errors': errors,
        }
    )
