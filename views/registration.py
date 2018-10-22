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
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from base.models import entity_version
from base.models.enums import entity_type
from continuing_education.forms.address import AddressForm
from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.views.common import display_errors


@login_required
def list_registrations(request):
    faculty_filter = int(request.GET.get("faculty", 0))
    if faculty_filter:
        admission_list = Admission.objects.filter(
            faculty=faculty_filter,
            state=admission_state_choices.ACCEPTED
        ).order_by(
            'person_information'
        )
    else:
        admission_list = Admission.objects.filter(
            state=admission_state_choices.ACCEPTED
        ).order_by(
            'person_information'
        )
    faculties = entity_version.find_latest_version(datetime.now()).filter(entity_type=entity_type.FACULTY)
    paginator = Paginator(admission_list, 10)
    page = request.GET.get('page')
    try:
        admissions = paginator.page(page)
    except PageNotAnInteger:
        admissions = paginator.page(1)
    except EmptyPage:
        admissions = paginator.page(paginator.num_pages)
    return render(request, "registrations.html", {
        'admissions': admissions,
        'faculties': faculties,
        'active_faculty': faculty_filter
    })


@login_required
def registration_detail(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    return render(
        request,
        "registration_detail.html",
        {
            'admission': admission,
        }
    )


@login_required
def registration_edit(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    form = RegistrationForm(request.POST or None, instance=admission)
    billing_address_form = AddressForm(request.POST or None, instance=admission.billing_address, prefix="billing")
    residence_address_form = AddressForm(request.POST or None, instance=admission.residence_address, prefix="residence")
    errors = []
    if form.is_valid() and billing_address_form.is_valid() and residence_address_form.is_valid():
        billing_address, created = Address.objects.get_or_create(**billing_address_form.cleaned_data)
        residence_address, created = Address.objects.get_or_create(**residence_address_form.cleaned_data)
        admission = form.save(commit=False)
        admission.billing_address = billing_address
        admission.residence_address = residence_address
        admission.save()
        return redirect(reverse('registration_detail', kwargs={'admission_id':admission_id}))
    else:
        errors.append(form.errors)
        display_errors(request, errors)

    return render(
        request,
        'registration_form.html',
        {
            'admission': admission,
            'form': form,
            'billing_address_form': billing_address_form,
            'residence_address_form': residence_address_form,
            'errors': errors,
        }
    )
