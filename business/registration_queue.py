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
import json
import logging

import pika
import pika.exceptions
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from base.views.common import display_error_messages
from continuing_education.business.perms import is_continuing_education_manager
from continuing_education.models.admission import Admission
from continuing_education.models.enums import ucl_registration_state_choices
from continuing_education.views.common import save_and_create_revision, get_revision_messages, \
    UCL_REGISTRATION_SENDED, UCL_REGISTRATION_REGISTERED, UCL_REGISTRATION_REJECTED
from osis_common.queue.queue_sender import send_message

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_json_for_epc(admission):
    return {
        'name': admission.person_information.person.last_name,
        'first_name': admission.person_information.person.first_name,
        'birth_date': admission.person_information.birth_date.strftime("%d/%m/%Y"),
        'birth_location': admission.person_information.birth_location,
        'birth_country_iso_code': admission.person_information.birth_country.iso_code,
        'sex': admission.person_information.person.gender,
        'civil_state': admission.marital_status,
        'nationality_iso_code': admission.citizenship.name,
        'mobile_number': admission.phone_mobile,
        'telephone_number': admission.residence_phone,
        'private_email': admission.email,
        'private_address': format_address_for_json(admission.residence_address),
        'staying_address': format_address_for_json(admission.address),
        'national_registry_number': admission.national_registry_number,
        'id_card_number': admission.id_card_number,
        'passport_number': admission.passport_number,
        'formation_code': admission.formation.acronym,
        'formation_academic_year': str(admission.academic_year.year),
        'student_case_uuid': str(admission.uuid)
    }


def format_address_for_json(address):
    if address:
        return {
            'street': address.location,
            'locality': address.city,
            'postal_code': address.postal_code,
            'country_name': address.country.name if address.country else '',
            'country_iso_code': address.country.iso_code if address.country else ''
        }
    return dict.fromkeys(
        ['street', 'locality', 'postal_code', 'country_name', 'country_iso_code'],
        ''
    )


def save_role_registered_in_admission(data):
    data = json.loads(data)
    admission = get_object_or_404(Admission, uuid=data['student_case_uuid'])
    if data['success']:
        admission.ucl_registration_complete = ucl_registration_state_choices.REGISTERED
        save_and_create_revision(None, get_revision_messages(UCL_REGISTRATION_REGISTERED), admission)
    else:
        admission.ucl_registration_complete = ucl_registration_state_choices.REJECTED
        save_and_create_revision(None, get_revision_messages(UCL_REGISTRATION_REJECTED), admission)


def send_admission_to_queue(request, admission):
    data = get_json_for_epc(admission)
    credentials = pika.PlainCredentials(settings.QUEUES.get('QUEUE_USER'),
                                        settings.QUEUES.get('QUEUE_PASSWORD'))
    rabbit_settings = pika.ConnectionParameters(settings.QUEUES.get('QUEUE_URL'),
                                                settings.QUEUES.get('QUEUE_PORT'),
                                                settings.QUEUES.get('QUEUE_CONTEXT_ROOT'),
                                                credentials)
    try:
        connect = pika.BlockingConnection(rabbit_settings)
        channel = connect.channel()
        queue_name = settings.QUEUES.get('QUEUES_NAME').get('IUFC_TO_EPC')
        send_message(queue_name, data, connect, channel)
        admission.ucl_registration_complete = ucl_registration_state_choices.SENDED
        save_and_create_revision(request.user, get_revision_messages(UCL_REGISTRATION_SENDED), admission)
    except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed, pika.exceptions.AMQPError):
        logger.exception(_('Could not send admission json with uuid %(uuid)s in queue') % {'uuid': admission.uuid})
        display_error_messages(
            request, _('Could not send admission json with uuid %(uuid)s in queue') % {'uuid': admission.uuid}
        )


@login_required
@user_passes_test(is_continuing_education_manager)
def inject_admission_to_epc(request, admission_id):
    redirection = request.META.get('HTTP_REFERER')
    admission = Admission.objects.get(id=admission_id)
    send_admission_to_queue(request, admission)
    return HttpResponseRedirect(redirection)
