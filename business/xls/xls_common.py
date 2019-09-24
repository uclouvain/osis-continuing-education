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
from django.utils.translation import gettext_lazy as _


def form_filters(form):
    criteria = {}
    if form:
        for field_name, field in form.fields.items():
            if form.cleaned_data[field_name]:
                criteria[field.label] = form.cleaned_data[field_name]
    return criteria


def get_titles_admission():
    return [
        str(_('Name')),
        str(_('First name')),
        str(_('Email')),
        str(_('State')),
        str(_('Gender')),
        str(_('Citizenship')),
        str(_('Birth date')),
        str(_('Birth location')),
        str(_('Birth country')),
        str(_('Mobile phone')),
        str(_('Contact address')),
        str(_('High school diploma')),
        str(_('High school graduation year')),
        str(_('Last degree level')),
        str(_('Last degree institution')),
        str(_('Last degree graduation year')),
        str(_('Other educational background')),
        str(_('Professional status')),
        str(_('Current occupation')),
        str(_('Current employer')),
        str(_('Activity sector')),
        str(_('Past professional activities')),
        str(_('Motivation')),
        str(_('Professional and personal interests')),
        str(_('Formation')),
        str(_('Training aid')),
        str(_('Faculty')),
        str(_('Formation administrator(s)')),
        str(_('Awareness')),
    ]


def extract_xls_data_from_admission(admission):
    return [
        admission.person_information.person.last_name,
        admission.person_information.person.first_name,
        admission.email,
        _(admission.state) if admission.state else '',
        admission.person_information.person.get_gender_display() if admission.person_information.person.gender else '',
        admission.citizenship.name.upper() if admission.citizenship else '',
        admission.person_information.person.birth_date,
        admission.person_information.birth_location.upper() if admission.person_information.birth_location else '',
        admission.person_information.birth_country.name.upper() if admission.person_information.birth_country else '',
        admission.phone_mobile,
        admission.complete_contact_address,
        _('Yes') if admission.high_school_diploma else _('No'),
        admission.high_school_graduation_year,
        admission.last_degree_level,
        admission.last_degree_institution,
        admission.last_degree_graduation_year,
        admission.other_educational_background if admission.other_educational_background else '',
        admission.get_professional_status_display() if admission.professional_status else '',
        admission.current_occupation if admission.current_occupation else '',
        admission.current_employer if admission.current_employer else '',
        admission.get_activity_sector_display() if admission.activity_sector else '',
        admission.past_professional_activities if admission.past_professional_activities else '',
        admission.motivation if admission.motivation else '',
        admission.professional_personal_interests if admission.professional_personal_interests else '',
        admission.formation.acronym,
        _('Yes') if admission.formation.training_aid else _('No'),
        admission.get_faculty() if admission.get_faculty() else '',
        admission.formation.formation_administrators,
        admission.awareness_list
    ]


def get_titles_registration():
    return [
        str(_('Registration type')),
        str(_('Head office name')),
        str(_('Company number')),
        str(_('VAT number')),
        str(_('Billing address')),
        str(_('National registry number')),
        str(_('ID card number')),
        str(_('Passport number')),
        str(_('Marital status')),
        str(_('Spouse name')),
        str(_('Children number')),
        str(_('Previous uclouvain registration')),
        str(_('Previous NOMA')),
        str(_('Residence address')),
        str(_('Residence phone')),
        str(_('UCLouvain registration complete')),
        str(_('Payment complete')),
        str(_('Registration file received')),
        str(_('Formation spreading')),
        str(_('Prior experience validation')),
        str(_('Assessment presented')),
        str(_('Assessment succeeded')),
        str(_('Diploma produced')),
        str(_('Comment')),
    ]


def extract_xls_data_from_registration(registration):
    return extract_xls_data_from_admission(registration) + [
        registration.get_registration_type_display() if registration.registration_type else '',
        registration.head_office_name if registration.head_office_name else '',
        registration.company_number if registration.company_number else '',
        registration.vat_number if registration.vat_number else '',
        registration.complete_billing_address,
        registration.national_registry_number if registration.national_registry_number else '',
        registration.id_card_number if registration.id_card_number else '',
        registration.passport_number if registration.passport_number else '',
        registration.get_marital_status_display() if registration.marital_status else '',
        registration.spouse_name if registration.spouse_name else '',
        registration.children_number if registration.children_number else '',
        registration.previous_ucl_registration if registration.previous_ucl_registration else '',
        registration.previous_noma if registration.previous_noma else '',
        registration.complete_residence_address,
        registration.residence_phone if registration.residence_phone else '',
        _('Yes') if registration.ucl_registration_complete else _('No'),
        _('Yes') if registration.payment_complete else _('No'),
        _('Yes') if registration.registration_file_received else _('No'),
        _('Yes') if registration.formation_spreading else _('No'),
        _('Yes') if registration.prior_experience_validation else _('No'),
        _('Yes') if registration.assessment_presented else _('No'),
        _('Yes') if registration.assessment_succeeded else _('No'),
        _('Yes') if registration.diploma_produced else _('No'),
        registration.comment if registration.comment else '',
    ]
