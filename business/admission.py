##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext as _

from osis_common.messaging import message_config
from osis_common.messaging import send_message as message_service

CONTINUING_EDUCATION_MANAGERS_GROUP = "continuing_education_managers"


def send_state_changed_email(admission):
    person = admission.person_information.person
    send_email(
        template_references={
            'html': 'iufc_participant_state_changed_{}_html'.format(admission.state.lower()),
            'txt': 'iufc_participant_state_changed_{}_txt'.format(admission.state.lower()),
        },
        template_data={
            'first_name': admission.person_information.person.first_name,
            'last_name': admission.person_information.person.last_name,
            'formation': admission.formation,
            'state': _(admission.state)
        },
        subject_data={
            'state': _(admission.state)
        },
        receivers=[
            message_config.create_receiver(
                person.id,
                person.email,
                None
            )
        ],
    )


def send_admission_submitted_email(admission):
    managers = _get_continuing_education_managers()
    send_email(
        template_references={
            'html': 'iufc_admin_admission_submitted_html',
            'txt': 'iufc_admin_admission_submitted_txt',
        },
        template_data={
            'first_name': admission.person_information.person.first_name,
            'last_name': admission.person_information.person.last_name,
            'formation': admission.formation,
            'state': _(admission.state)
        },
        subject_data={
            'formation': admission.formation,
            'state': _(admission.state),
        },
        receivers=[
            message_config.create_receiver(
                manager.id,
                manager.email,
                None
            )
            for manager in managers
        ],
    )


def send_admission_created_email(admission):
    participant = admission.person_information.person
    send_email(
        template_references={
            'html': 'iufc_participant_admission_created_html',
            'txt': 'iufc_participant_admission_created_txt',
        },
        template_data={
            'formation': admission.formation.acronym,
        },
        subject_data={},
        receivers=[
            message_config.create_receiver(
                participant.id,
                participant.email,
                None
            )
        ],
    )


def send_email(template_references, receivers, template_data, subject_data):
    message_content = message_config.create_message_content(
        template_references['html'],
        template_references['txt'],
        [],
        receivers,
        template_data,
        subject_data
    )
    message_service.send_messages(message_content)


def _get_continuing_education_managers():
    return User.objects.filter(groups=Group.objects.get(name=CONTINUING_EDUCATION_MANAGERS_GROUP))
