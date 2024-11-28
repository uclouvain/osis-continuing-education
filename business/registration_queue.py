##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import json
import logging

import pika
import pika.exceptions
from django.conf import settings
from osis_common.queue.queue_utils import get_pika_connexion_parameters
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import permission_required

from base.views.common import display_error_messages
from continuing_education.models.admission import Admission
from continuing_education.models.admission import admission_getter
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.views.common import save_and_create_revision, get_revision_messages, \
    UCL_REGISTRATION_SENDED, UCL_REGISTRATION_REJECTED, UCL_REGISTRATION_STATE_CHANGED, \
    UCL_REGISTRATION_REGISTERED
from osis_common.queue.queue_sender import send_message


MAX_LENGTH_FOR_LAST_NAME_FIELD_IN_EPC = 40
MAX_LENGTH_FOR_FIRST_NAME_FIELD_IN_EPC = 20
MAX_LENGTH_FOR_STREET_FIELD_IN_EPC = 50
MAX_LENGTH_FOR_POSTAL_CODE_FIELD_IN_EPC = 12
MAX_LENGTH_FOR_LOCALITY_FIELD_IN_EPC = 40


logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_json_for_epc(admission):
    addresses_are_different = admission.address != admission.residence_address
    return {
        'name': admission.person_information.person.last_name[0:MAX_LENGTH_FOR_LAST_NAME_FIELD_IN_EPC],
        'first_name': admission.person_information.person.first_name[0:MAX_LENGTH_FOR_FIRST_NAME_FIELD_IN_EPC],
        'birth_date': admission.person_information.birth_date.strftime("%d/%m/%Y"),
        'birth_location': admission.person_information.birth_location,
        'birth_country_iso_code': admission.person_information.birth_country.iso_code,
        # TODO:: Fix continuing_education to manage gender/sex correctly, then inject sex instead of gender
        'sex': _gender_to_sex(admission.person_information.person.gender),
        'civil_state': admission.marital_status,
        'nationality_iso_code': admission.citizenship.iso_code if admission.citizenship else '',
        'mobile_number': admission.phone_mobile,
        'telephone_number': admission.residence_phone,
        'private_email': admission.email,
        'private_address': format_address_for_json(admission.address),
        'staying_address': format_address_for_json(admission.residence_address) if addresses_are_different else {},
        'national_registry_number': admission.national_registry_number,
        'id_card_number': admission.id_card_number,
        'passport_number': admission.passport_number,
        'formation_code': admission.formation.acronym,
        'formation_academic_year': str(admission.academic_year.year),
        'student_case_uuid': str(admission.uuid)
    }


def _gender_to_sex(gender):
    if gender == "H":
        return "M"
    elif gender == "F":
        return "F"
    else:
        raise ValueError("Gender for continuing_education must be H or F.")


def format_address_for_json(address):
    if address:
        return {
            'street': address.location[0:MAX_LENGTH_FOR_STREET_FIELD_IN_EPC],
            'locality': address.city[0:MAX_LENGTH_FOR_LOCALITY_FIELD_IN_EPC],
            'postal_code': address.postal_code[0:MAX_LENGTH_FOR_POSTAL_CODE_FIELD_IN_EPC],
            'country_name': address.country.name if address.country else '',
            'country_iso_code': address.country.iso_code if address.country else ''
        }
    return dict.fromkeys(
        ['street', 'locality', 'postal_code', 'country_name', 'country_iso_code'],
        ''
    )


def save_role_registered_in_admission(data):
    data = json.loads(data.decode("utf-8").replace("\'", "\""))
    admission = get_object_or_404(Admission, uuid=data['student_case_uuid'])
    if data['success']:
        registration_status = data.get('registration_status')
        admission.ucl_registration_complete = registration_status
        admission.noma = data.get('registration_id')
        if registration_status == UCLRegistrationState.INSCRIT.name:
            message = UCL_REGISTRATION_REGISTERED
        else:
            UCL_REGISTRATION_STATE_CHANGED['text'] += admission.get_ucl_registration_complete_display()
            message = UCL_REGISTRATION_STATE_CHANGED
    else:
        admission.ucl_registration_complete = UCLRegistrationState.REJECTED.name
        admission.ucl_registration_error = data['message']
        UCL_REGISTRATION_REJECTED['text'] += admission.get_ucl_registration_error_display()
        message = UCL_REGISTRATION_REJECTED

    save_and_create_revision(get_revision_messages(message), admission)


def send_admission_to_queue(request, admission):
    data = get_json_for_epc(admission)
    try:
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('IUFC_TO_EPC')
        conn_params = get_pika_connexion_parameters(queue_name=queue_name)
        connect = pika.BlockingConnection(conn_params)
        channel = connect.channel()
        send_message(queue_name, data, connect, channel)
        admission.ucl_registration_complete = UCLRegistrationState.SENDED.name
        save_and_create_revision(get_revision_messages(UCL_REGISTRATION_SENDED), admission, request.user)
    except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed, pika.exceptions.AMQPError):
        logger.exception(_('Could not send admission json with uuid %(uuid)s in queue') % {'uuid': admission.uuid})
        display_error_messages(
            request, _('Could not send admission json with uuid %(uuid)s in queue') % {'uuid': admission.uuid}
        )


@login_required
@permission_required('continuing_education.inject_admission_to_epc', fn=admission_getter)
def inject_admission_to_epc(request, admission_id):
    redirection = request.headers.get('referer')
    admission = Admission.objects.get(id=admission_id)
    send_admission_to_queue(request, admission)
    return HttpResponseRedirect(redirection)
