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
from datetime import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models import entity_version
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type
from base.models.person import Person
from base.views.common import display_success_messages, display_error_messages
from continuing_education.forms.account import ContinuingEducationPersonForm
from continuing_education.forms.address import AddressForm
from continuing_education.forms.admission import AdmissionForm, RejectedAdmissionForm
from continuing_education.forms.person import PersonForm
from continuing_education.models import continuing_education_person
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT
from continuing_education.models.exceptions import TooLongFilenameException
from continuing_education.models.file import File
from continuing_education.views.common import display_errors


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_admissions(request):
    faculty_filter = int(request.GET.get("faculty", 0))
    state_to_display = [SUBMITTED, REJECTED, WAITING]
    admission_list = Admission.objects.filter(
        state__in=state_to_display
    ).order_by('person_information')
    if faculty_filter:
        formations = _get_formations_by_faculty(faculty_filter)
        admission_list = admission_list.filter(
            formation__acronym__in=formations
        ).order_by('person_information')
    faculties = entity_version.find_latest_version(datetime.now()).filter(entity_type=entity_type.FACULTY)
    paginator = Paginator(admission_list, 10)
    page = request.GET.get('page')
    try:
        admissions = paginator.page(page)
    except PageNotAnInteger:
        admissions = paginator.page(1)
    except EmptyPage:
        admissions = paginator.page(paginator.num_pages)
    return render(request, "admissions.html", {
        'admissions': admissions,
        'faculties': faculties,
        'active_faculty': faculty_filter
    })


def _get_formations_by_faculty(faculty):
    entity = EntityVersion.objects.filter(id=faculty).first().entity
    entities_child = EntityVersion.objects.filter(parent=entity)
    formations = EducationGroupYear.objects.filter(
        management_entity=entity
    )
    for child in entities_child:
        formations |= EducationGroupYear.objects.filter(
            management_entity=child.entity
        )
    formations = [formation.acronym for formation in formations]
    return formations


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def admission_detail(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    files = File.objects.all().filter(admission=admission_id)
    accepted_states = admission_state_choices.NEW_ADMIN_STATE[admission.state]
    states = accepted_states.get('choices', ())
    adm_form = AdmissionForm(
        request.POST or None,
        instance=admission,
    )

    if request.method == 'POST' and request.FILES:
        return _upload_file(request, admission)

    rejected_adm_form = RejectedAdmissionForm(
        request.POST or None,
        instance=admission,
        )

    if adm_form.is_valid():
        return _change_state(adm_form, accepted_states, admission, rejected_adm_form)

    return render(
        request, "admission_detail.html",
        {
            'admission': admission,
            'files': files,
            'states': states,
            'admission_form': adm_form,
            'rejected_adm_form': rejected_adm_form,
        }
    )


def _change_state(adm_form, accepted_states, admission, rejected_adm_form):
    new_state = adm_form.cleaned_data['state']
    if new_state in accepted_states.get('states', []):
        return _new_state_management(adm_form, admission, new_state, rejected_adm_form)


def _upload_file(request, admission):
    my_file = request.FILES['myfile']
    person = Person.objects.get(user=request.user)
    file_to_admission = File(
        admission=admission,
        path=my_file,
        name=my_file.name,
        size=my_file.size,
        uploaded_by=person
    )
    try:
        file_to_admission.save()
        display_success_messages(request, _("The document is uploaded correctly"))
    except TooLongFilenameException as e:
        display_error_messages(request, str(e))
    except Exception as e:
        display_error_messages(request, _("A problem occured : the document is not uploaded"))
    return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}) + '#documents')


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def download_file(request, admission_id, file_id):
    file = File.objects.get(pk=file_id)
    filename = file.name.split('/')[-1]
    response = HttpResponse(file.path, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def delete_file(request, admission_id, file_id):
    file = File.objects.filter(id=file_id)
    try:
        file.delete()
        display_success_messages(request, _("File correctly deleted"))
    except Exception as e:
        display_error_messages(request, _("A problem occured during delete"))
    return redirect(reverse('admission_detail', kwargs={'admission_id': admission_id}) + '#documents')


@login_required
@permission_required('continuing_education.change_admission', raise_exception=True)
def admission_form(request, admission_id=None):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    states = admission_state_choices.NEW_ADMIN_STATE[admission.state].get('choices', ()) if admission else None
    base_person = admission.person_information.person if admission else None
    base_person_form = PersonForm(request.POST or None, instance=base_person)
    person_information = continuing_education_person.find_by_person(person=base_person)
    # TODO :: get last admission address if it exists instead of None
    address = admission.address if admission else None
    state = admission.state if admission else SUBMITTED
    adm_form = AdmissionForm(request.POST or None, instance=admission, initial={'state': state})
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
            'admission_id': admission_id,
            'admission_form': adm_form,
            'person_form': person_form,
            'address_form': address_form,
            'base_person_form': base_person_form,
            'state': state,
            'states': states
        }
    )


def _new_state_management(adm_form, admission, new_state, rejected_adm_form):
    if new_state == REJECTED:
        if rejected_adm_form.is_valid():
            rejected_adm_form.save()
    else:
        adm_form.save()

    if new_state == DRAFT:
        return redirect(reverse('admission'))

    return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}))
