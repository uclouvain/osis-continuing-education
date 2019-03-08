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
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.translation import ugettext_lazy as _

from base.views.common import display_success_messages, display_error_messages
from continuing_education.business.xls.xls_archive import create_xls
from continuing_education.forms.search import ArchiveFilterForm
from continuing_education.models.admission import Admission
from continuing_education.views.common import get_object_list, has_selected_items


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_archives(request):
    search_form = ArchiveFilterForm(data=request.POST)
    archive_list = []

    if search_form.is_valid():
        archive_list = search_form.get_archives()

    if request.POST.get('xls_status') == "xls_archives":
        return create_xls(request.user, archive_list, search_form)

    return render(request, "archives.html", {
        'archives': get_object_list(request, archive_list),
        'search_form': search_form
    })


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def archive_procedure(request, admission_id):
    redirection = request.META.get('HTTP_REFERER')
    admission = _switch_archived_state(admission_id)
    _set_success_message(request, admission.is_registration, False, admission.archived)
    return HttpResponseRedirect(redirection)


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def archives_procedure(request):
    selected_admissions_id = request.POST.getlist("selected_action", default=[])
    redirection = request.META.get('HTTP_REFERER')
    is_registration = 'registration' in redirection
    if has_selected_items(selected_admissions_id):
        _mark_folders_as_archived(is_registration, request, selected_admissions_id)
        return redirect(reverse('archive'))
    else:
        _set_error_message(is_registration, request)
        return HttpResponseRedirect(redirection)


def _mark_folders_as_archived(is_registration, request, selected_admissions_id):
    for admission_id in selected_admissions_id:
        _mark_as_archived(admission_id)
    _set_success_message(request, is_registration, len(selected_admissions_id) > 1)


def _set_success_message(request, is_registration, is_plural, admission_archived=True):
    success_msg = "{}{} {} {}".format(
        _('Registration') if is_registration else _('Admission'),
        's' if is_plural else '',
        _('are now') if is_plural else _('is now'),
        _('archived') if admission_archived else _('unarchived')
    )

    display_success_messages(request, success_msg)


def _mark_as_archived(admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    _set_archived_state(admission, True)


def _set_archived_state(admission, archived_state):
    if admission:
        admission.archived = archived_state
        admission.save()


def _set_error_message(is_registration, request):
    if is_registration:
        error_msg = _('Please select at least one registration to archive')
    else:
        error_msg = _('Please select at least one admission to archive')
    display_error_messages(request, error_msg)


def _switch_archived_state(admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    _set_archived_state(admission, not admission.archived)
    return admission
