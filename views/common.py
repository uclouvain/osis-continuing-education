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
import operator
from functools import reduce

import reversion
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Prefetch, Q
from django.utils.translation import gettext_lazy as _
from reversion.models import Version

from continuing_education.models.admission import Admission
from continuing_education.models.enums.admission_state_choices import ACCEPTED, VALIDATED, REGISTRATION_SUBMITTED, \
    SUBMITTED

UCL_REGISTRATION_COMPLETE = {'icon': 'fas fa-university', 'text': _('UCLouvain registration complete')}
REGISTRATION_FILE_RECEIVED = {'icon': 'fas fa-receipt', 'text': _('Registration file received')}
FILE_ARCHIVED = {'icon': 'fas fa-folder-plus', 'text': _('File archived')}
FILE_UNARCHIVED = {'icon': 'fas fa-folder-minus', 'text': _('File unarchived')}
ADMISSION_CREATION = {'icon': 'fas fa-plus-circle', 'text': _('Creation of the admission')}
REGISTRATION_VALIDATED = {'icon': 'fas fa-check-double', 'text': _('Registration validated')}
ADMISSION_ACCEPTED = {'icon': 'fas fa-check', 'text': _('Admission accepted')}
SUBMITTED_REGISTRATION = {'icon': 'far fa-paper-plane', 'text': _('Registration submitted')}
SUBMITTED_ADMISSION = {'icon': 'far fa-paper-plane', 'text': _('Admission submitted')}

STATE_CHANGED = {'icon': 'fas fa-exchange-alt', 'text': ''}
STATE_CHANGED_MESSAGE = _('State : %(old_state)s ► %(new_state)s')

MAIL = {'icon': 'far fa-envelope-open', 'text': ''}
MAIL_MESSAGE = _('Mail sent to %(receiver)s')

UCL_REGISTRATION_SENDED = {'icon': 'glyphicon glyphicon-time', 'text': _('Folder sended to EPC : waiting for response')}
UCL_REGISTRATION_REJECTED = {'icon': 'glyphicon glyphicon-remove',
                             'text': _('Folder injection into EPC failed : %(reasons)s') % {'reasons': ''}}
UCL_REGISTRATION_REGISTERED = {'icon': 'glyphicon glyphicon-ok-circle',
                               'text': _('Folder injection into EPC succeeded : UCLouvain registration completed')}
UCL_REGISTRATION_ON_DEMAND = {'icon': 'glyphicon glyphicon-question-sign',
                              'text': _('Folder injection into EPC succeeded : UCLouvain registration on demand')}

VERSION_MESSAGES = [
    UCL_REGISTRATION_COMPLETE['text'],
    REGISTRATION_FILE_RECEIVED['text'],
    FILE_ARCHIVED['text'],
    FILE_UNARCHIVED['text'],
    ADMISSION_CREATION['text'],
    REGISTRATION_VALIDATED['text'],
    ADMISSION_ACCEPTED['text'],
    SUBMITTED_REGISTRATION['text'],
    SUBMITTED_ADMISSION['text'],
    _('Mail sent to '),
    ' ► ',
    UCL_REGISTRATION_SENDED['text'],
    UCL_REGISTRATION_REJECTED['text'],
    UCL_REGISTRATION_REGISTERED['text'],
    UCL_REGISTRATION_ON_DEMAND['text'],
]


def display_errors(request, errors):
    for error in errors:
        for key, value in error.items():
            messages.add_message(request, messages.ERROR, "{} : {}".format(_(key), value[0]), "alert-danger")


def get_object_list(request, objects):
    if objects is None:
        objects = []
    paginator = Paginator(objects, 10)
    page = request.GET.get('page')

    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        object_list = paginator.page(1)
    except EmptyPage:
        object_list = paginator.page(paginator.num_pages)
    return object_list


def save_and_create_revision(message, admission=None, user=None):
    with reversion.create_revision():
        existing_message = reversion.get_comment()
        if admission:
            admission.save()
        if user:
            reversion.set_user(user)
        append_message = existing_message + " <br> &nbsp; " if existing_message else ''
        reversion.set_comment(append_message + message if message else existing_message)


def _get_icon(message):
    return '<i class="{type}"></i> '.format(type=message['icon'])


def get_revision_messages(message, msgs=None):
    return ("<br>" if msgs else '') + _get_icon(message) + str(message['text'])


def get_appropriate_revision_message(form):
    msgs = []
    if 'ucl_registration_complete' in form.changed_data and form.cleaned_data['ucl_registration_complete']:
        msgs.append(get_revision_messages(UCL_REGISTRATION_COMPLETE, msgs))
    if 'registration_file_received' in form.changed_data and form.cleaned_data['registration_file_received']:
        msgs.append(get_revision_messages(REGISTRATION_FILE_RECEIVED, msgs))
    return ' '.join(msgs) if msgs else ''


def get_versions(admission):
    query = reduce(operator.or_, (Q(revision__comment__contains=item) for item in VERSION_MESSAGES))
    reversions = Version.objects.filter(
        content_type=ContentType.objects.get_for_model(Admission),
        object_id=admission.id,
    ).filter(query).select_related(
        "revision",
        "revision__user",
    ).prefetch_related(
        Prefetch(
            "revision__user__person",
            to_attr="author"
        )
    ).select_related('revision__user__person').order_by(
        "-revision__date_created"
    )
    return reversions


def get_valid_state_change_message(instance):
    if instance.state == ACCEPTED:
        message = ADMISSION_ACCEPTED
    elif instance.state == VALIDATED:
        message = REGISTRATION_VALIDATED
    elif instance.state == REGISTRATION_SUBMITTED:
        message = SUBMITTED_REGISTRATION
    elif instance.state == SUBMITTED:
        message = SUBMITTED_ADMISSION
    else:
        STATE_CHANGED['text'] = STATE_CHANGED_MESSAGE % {
            'old_state': _(instance._original_state),
            'new_state': _(instance.state)
        }
        message = STATE_CHANGED
    return message
