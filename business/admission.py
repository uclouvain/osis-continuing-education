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
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import FACULTY
from osis_common.messaging import message_config
from osis_common.messaging import send_message as message_service

CONTINUING_EDUCATION_MANAGERS_GROUP = "continuing_education_managers"


def send_state_changed_email(admission, connected_user=None):
    person = admission.person_information.person
    mails = _get_managers_mails(admission.formation)
    send_email(
        template_references={
            'html': 'iufc_participant_state_changed_{}_html'.format(admission.state.lower()),
            'txt': 'iufc_participant_state_changed_{}_txt'.format(admission.state.lower()),
        },
        data={
            'template': {
                'first_name': admission.person_information.person.first_name,
                'last_name': admission.person_information.person.last_name,
                'formation': admission.formation,
                'state': _(admission.state),
                'reason': admission.state_reason if admission.state_reason else '-',
                'mails': mails
            },
            'subject': {
                'state': _(admission.state)
            }
        },
        receivers=[
            message_config.create_receiver(
                person.id,
                person.email,
                None
            )
        ],
        connected_user=connected_user
    )


def send_admission_submitted_email_to_admin(admission):
    relative_path = reverse('admission_detail', kwargs={'admission_id': admission.id})
    # No request here because we are in a post_save
    formation_url = 'https://{}{}'.format(Site.objects.get_current().domain, relative_path)

    managers = _get_continuing_education_managers()
    send_email(
        template_references={
            'html': 'iufc_admin_admission_submitted_html',
            'txt': 'iufc_admin_admission_submitted_txt',
        },
        data={
            'template': {
                'first_name': admission.person_information.person.first_name,
                'last_name': admission.person_information.person.last_name,
                'formation': admission.formation,
                'state': _(admission.state),
                'formation_link': formation_url,
            },
            'subject': {
                'formation': admission.formation.acronym,
            }
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


def send_admission_submitted_email_to_participant(admission):
    participant = admission.person_information.person
    mails = _get_managers_mails(admission.formation)
    send_email(
        template_references={
            'html': 'iufc_participant_admission_submitted_html',
            'txt': 'iufc_participant_admission_submitted_txt',
        },
        data={
            'template': {
                'formation': admission.formation.acronym,
                'admission_data': _get_formatted_admission_data(admission),
                'mails': mails
            },
            'subject': {}
        },
        receivers=[
            message_config.create_receiver(
                participant.id,
                participant.email,
                None
            )
        ],
    )


def send_invoice_uploaded_email(admission):
    participant = admission.person_information.person
    mails = _get_managers_mails(admission.formation)
    send_email(
        template_references={
            'html': 'iufc_participant_invoice_uploaded_html',
            'txt': 'iufc_participant_invoice_uploaded_txt',
        },
        data={
            'template': {
                'formation': admission.formation.acronym,
                'mails': mails
            },
            'subject': {}
        },
        receivers=[
            message_config.create_receiver(
                participant.id,
                participant.email,
                None
            )
        ],
    )


def send_email(template_references, receivers, data, connected_user=None):
    message_content = message_config.create_message_content(
        template_references['html'],
        template_references['txt'],
        [],
        receivers,
        data['template'],
        data['subject']
    )
    message_service.send_messages(message_content, connected_user)


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
        "{} : {}".format(_('Professional and personal interests'),
                         _value_or_empty(admission.professional_personal_interests)),
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


def get_management_faculty(education_group_yr):
    if education_group_yr:
        management_entity = education_group_yr.management_entity
        entity = EntityVersion.objects.filter(entity=management_entity).first()
        if entity and entity.entity_type == FACULTY:
            return management_entity
        else:
            return _get_faculty_parent(management_entity)
    else:
        return None


def _get_faculty_parent(management_entity):
    faculty = EntityVersion.objects.filter(entity=management_entity).first()
    if faculty:
        return faculty.parent


def _get_managers_mails(formation):
    managers_mail = formation.managers.all().order_by('last_name').values_list('email', flat=True) \
        if formation else []
    return _(" or ").join(managers_mail)


def check_required_field_for_participant(obj, meta, fields_required, extra=None):
    if obj:
        return _check_fields(fields_required, meta, obj, extra)
    else:

        return {response[key]: meta.get_field(key).verbose_name}


def _check_fields(fields_required, meta, obj, extra):
    response = {}
    for key in fields_required:
        value = getattr(obj, key, None)
        if value is None or (isinstance(value, str) and len(value) == 0):
            _build_validation_msg(extra, key, meta, response)
    return response


def _build_validation_msg(extra, key, meta, response):
    if extra:
        extra_key = '{}_{}'.format(key, extra.strip())
        response[extra_key] = '{} : {}'.format(extra, meta.get_field(key).verbose_name)
    else:
        response[key] = meta.get_field(key).verbose_name
