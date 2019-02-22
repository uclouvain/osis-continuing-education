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
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from continuing_education.business.xls.xls_registration import create_xls_registration
from continuing_education.forms.address import AddressForm
from continuing_education.forms.registration import RegistrationForm
from continuing_education.forms.search import RegistrationFilterForm
from continuing_education.models.address import Address
from continuing_education.models.admission import Admission
from continuing_education.views.common import display_errors


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_registrations(request):
    search_form = RegistrationFilterForm(data=request.POST)

    if search_form.is_valid():
        admission_list = search_form.get_registrations()

    if request.POST.get('xls_status') == "xls_registrations":
        return create_xls_registration(request.user, admission_list, search_form)

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
        'search_form': search_form
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
@permission_required('continuing_education.change_admission', raise_exception=True)
def registration_edit(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    form = RegistrationForm(request.POST or None, instance=admission)
    billing_address_form = AddressForm(request.POST or None, instance=admission.billing_address, prefix="billing")
    residence_address_form = AddressForm(request.POST or None, instance=admission.residence_address, prefix="residence")

    address = admission.address
    residence_address = admission.residence_address
    billing_address = admission.billing_address

    errors = []
    if form.is_valid() and billing_address_form.is_valid() and residence_address_form.is_valid():
        use_address = {
            'for_billing': form.cleaned_data['use_address_for_billing'],
            'for_post': form.cleaned_data['use_address_for_post']
        }
        admission.residence_address = residence_address
        admission.billing_address = billing_address
        billing_address, residence_address = _update_or_create_billing_and_post_address(
            address,
            {'address': billing_address, 'form': billing_address_form},
            {'address': residence_address, 'form': residence_address_form},
            use_address,
        )
        admission = form.save(commit=False)
        admission.address = address
        admission.billing_address = billing_address
        admission.residence_address = residence_address
        admission.save()
        return redirect(reverse('admission_detail', kwargs={'admission_id': admission_id}) + "#registration")
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


def _update_or_create_billing_and_post_address(address, billing, residence, use_address):
    if use_address['for_billing']:
        billing['address'] = address
    elif billing['address'] == address:
        billing['address'], created = Address.objects.get_or_create(**billing['form'].cleaned_data)
    else:
        Address.objects.filter(id=billing['address'].id).update(**billing['form'].cleaned_data)

    if use_address['for_post']:
        residence['address'] = address
    elif residence['address'] == address:
        residence['address'], created = Address.objects.get_or_create(**residence['form'].cleaned_data)
    else:
        Address.objects.filter(id=residence['address'].id).update(**residence['form'].cleaned_data)
    return billing['address'], residence['address']
