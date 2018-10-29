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

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from base.models import entity_version
from base.models.enums import entity_type
from continuing_education.forms.account import ContinuingEducationPersonForm
from continuing_education.forms.address import AddressForm
from continuing_education.forms.admission import AdmissionForm
from continuing_education.forms.person import PersonForm
from continuing_education.models import continuing_education_person
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.views.common import display_errors


@login_required
def list_admissions(request):
    faculty_filter = int(request.GET.get("faculty",0))
    if faculty_filter:
        admission_list = Admission.objects.filter(faculty=faculty_filter).order_by('person_information')
    else:
        admission_list = Admission.objects.all().order_by('person_information')
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


@login_required
def admission_detail(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    return render(
        request, "admission_detail.html",
        {
            'admission': admission,
        }
    )


@login_required
def admission_form(request, admission_id=None):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    base_person = admission.person_information.person if admission else None
    base_person_form = PersonForm(request.POST or None, instance=base_person)
    person_information = continuing_education_person.find_by_person(person=base_person)
    # TODO :: get last admission address if it exists instead of None
    address = admission.address if admission else None
    adm_form = AdmissionForm(request.POST or None, instance=admission)
    person_form = ContinuingEducationPersonForm(request.POST or None, instance=person_information)
    address_form = AddressForm(request.POST or None, instance=address)

    if adm_form.is_valid() and person_form.is_valid() and address_form.is_valid():
        if address:
            address = address_form.save()
        else:
            address = Address(**address_form.cleaned_data)
            address.save()

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
        return redirect(reverse('admission_detail', kwargs={'admission_id':admission.pk}))

    else:
        errors = list(itertools.product(adm_form.errors, person_form.errors, address_form.errors))
        display_errors(request, errors)

    return render(
        request,
        'admission_form.html',
        {
            'admission_form': adm_form,
            'person_form': person_form,
            'address_form': address_form,
            'base_person_form': base_person_form
        }
    )
