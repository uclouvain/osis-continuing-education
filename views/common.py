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
from django.utils.translation import gettext_lazy as _, ugettext_lazy as _
from reversion.models import Version

from continuing_education.models.admission import Admission

UCL_REGISTRATION_COMPLETE = _('UCLouvain registration complete')
REGISTRATION_FILE_RECEIVED = _('Registration file received')
FILE_ARCHIVED = _('File archived')
FILE_UNARCHIVED = _('File unarchived')
ADMISSION_CREATION = _('Creation of the admission')
STATE_CHANGED = _('%(old_state)s to %(new_state)s')
REGISTRATION_VALIDATED = _('Registration validated')

VERSION_MESSAGES = [
    UCL_REGISTRATION_COMPLETE,
    REGISTRATION_FILE_RECEIVED,
    FILE_ARCHIVED,
    FILE_UNARCHIVED,
    ADMISSION_CREATION,
    REGISTRATION_VALIDATED,
    _(' to '),
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


def _save_and_create_revision(adm_form, request, message):
    with reversion.create_revision():
        adm_form.save()
        reversion.set_user(request.user)
        reversion.set_comment(message)


def _get_appropriate_revision_message(form):
    messages = []
    if 'ucl_registration_complete' in form.changed_data and form.cleaned_data['ucl_registration_complete']:
        messages.append(str(UCL_REGISTRATION_COMPLETE))
    if 'registration_file_received' in form.changed_data and form.cleaned_data['registration_file_received']:
        messages.append(str(REGISTRATION_FILE_RECEIVED))
    if 'archived' in form.changed_data and form.cleaned_data['archived']:
        messages.append(str(FILE_ARCHIVED))
    message = ', '.join(messages) if messages else ''
    return message


def _get_versions(admission):
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

    ).order_by(
        "-revision__date_created"
    )
    return reversions
