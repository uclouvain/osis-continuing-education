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
from django.shortcuts import get_object_or_404

from continuing_education.models.admission import Admission
from osis_common.queue.queue_sender import send_message

logger = logging.getLogger(settings.DEFAULT_LOGGER)


def get_json_for_epc(admission):
    return {
        'name': admission.person_information.person.last_name,
        'first_name': admission.person_information.person.first_name,
        'birth_date': admission.person_information.birth_date.strftime("%d/%m/%Y"),
        'birth_location': admission.person_information.birth_location,
        'birth_country': admission.person_information.birth_country.iso_code,
        'sex': admission.person_information.person.gender,
        'civil_state': admission.marital_status,
        'mobile_number': admission.phone_mobile,
        'telephone_number': admission.residence_phone,
        'private_email': admission.email,
        'private_address': format_address_for_json(admission.residence_address),
        'staying_address': format_address_for_json(admission.address),
        'national_registry_number': admission.national_registry_number,
        'id_card_number': admission.id_card_number,
        'passport_number': admission.passport_number,
        'formation_code': admission.formation.acronym,
        'formation_academic_year': str(admission.formation.academic_year),
        'student_case_uuid': str(admission.uuid)
    }


def format_address_for_json(address):
    return {
        'street_name': address.location,
        'locality': address.city,
        'postal_code': address.postal_code,
        'country_name': address.country.name if address.country else '',
        'country_iso_code': address.country.iso_code if address.country else ''
    }


def save_role_registered_in_admission(data):
    data = json.loads(data)
    if data['success']:
        admission = get_object_or_404(Admission, uuid=data['student_case_uuid'])
        admission.ucl_registration_complete = True
        admission.save()


def send_admission_to_queue(admission):
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
    except (RuntimeError, pika.exceptions.ConnectionClosed, pika.exceptions.ChannelClosed, pika.exceptions.AMQPError):
        logger.exception('Could not send admission json with uuid {} in queue'.format(admission.uuid))
