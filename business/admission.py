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
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

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
            'state': _(admission.state),
            'reason': admission.state_reason if admission.state_reason else '-',
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
    relative_path = reverse('admission_detail', kwargs={'admission_id': admission.id})
    # No request here because we are in a post_save
    formation_url = 'https://{}{}'.format(Site.objects.get_current().domain, relative_path)

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
            'state': _(admission.state),
            'formation_link': formation_url,
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
            'admission_data': _get_formatted_admission_data(admission)
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


def _get_formatted_admission_data(admission):
    return [
        "{} : {}".format(_('Last name'), _value_or_empty(admission.person_information.person.last_name)),
        "{} : {}".format(_('First name'), _value_or_empty(admission.person_information.person.first_name)),
        "{} : {}".format(_('Formation'), _value_or_empty(admission.formation.acronym)),
        "{} : {}".format(_('High school diploma'), _('Yes') if admission.high_school_diploma else _('No')),
        "{} : {}".format(_('High school graduation year'), _value_or_empty(admission.high_school_graduation_year)),
        "{} : {}".format(_('Last degree level'), _value_or_empty(admission.last_degree_level)),
        "{} : {}".format(_('Last degree field'), _value_or_empty(admission.last_degree_field)),
        "{} : {}".format(_('Last degree institution'), _value_or_empty(admission.last_degree_institution)),
        "{} : {}".format(_('Last degree graduation year'), _value_or_empty(admission.last_degree_graduation_year)),
        "{} : {}".format(_('Other educational background'), _value_or_empty(admission.other_educational_background)),
        "{} : {}".format(_('Professional status'), _value_or_empty(admission.professional_status)),
        "{} : {}".format(_('Current occupation'), _value_or_empty(admission.current_occupation)),
        "{} : {}".format(_('Current employer'), _value_or_empty(admission.current_employer)),
        "{} : {}".format(_('Activity sector'), _value_or_empty(admission.activity_sector)),
        "{} : {}".format(_('Past professional activities'), _value_or_empty(admission.past_professional_activities)),
        "{} : {}".format(_('Motivation'), _value_or_empty(admission.motivation)),
        "{} : {}".format(_('Professional impact'), _value_or_empty(admission.professional_impact)),
        "{} : {}".format(_('State'), _value_or_empty(_(admission.state))),
    ]


def _value_or_empty(value):
    return value or ''


def disable_existing_fields(form):
    fields_to_disable = ["birth_country", "birth_date", "gender"]

    for field in form.fields.keys():
        form.fields[field].initial = getattr(form.instance, field)
        form.fields[field].widget.attrs['readonly'] = True
        if field in fields_to_disable:
            form.fields[field].widget.attrs['disabled'] = True
