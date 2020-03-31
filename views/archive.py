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

from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.translation import gettext_lazy as _

from base.utils.cache import cache_filter
from base.views.common import display_success_messages, display_error_messages
from continuing_education.business.xls.xls_archive import create_xls
from continuing_education.forms.search import ArchiveFilterForm
from continuing_education.models.admission import Admission, filter_authorized_admissions, can_access_admission
from continuing_education.views.common import get_object_list, FILE_ARCHIVED, save_and_create_revision, \
    FILE_UNARCHIVED, get_revision_messages


@login_required
@permission_required('continuing_education.archive_admission', raise_exception=True)
@cache_filter(exclude_params=['xls_status'])
def list_archives(request):
    search_form = ArchiveFilterForm(data=request.GET, user=request.user)
    archive_list = []

    if search_form.is_valid():
        archive_list = search_form.get_archives()

    archive_list = filter_authorized_admissions(request.user, archive_list)

    if request.GET.get('xls_status') == "xls_archives":
        return create_xls(request.user, archive_list, search_form)

    return render(request, "archives.html", {
        'archives': get_object_list(request, archive_list),
        'archives_number': len(archive_list),
        'search_form': search_form
    })


@login_required
@permission_required('continuing_education.archive_admission', raise_exception=True)
def archive_procedure(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id) if admission_id else None
    can_access_admission(request.user, admission)
    if admission.is_draft():
        raise PermissionDenied
    redirection = request.META.get('HTTP_REFERER')
    admission = _switch_archived_state(request.user, admission_id)
    _set_success_message(request, False, admission.archived)
    return HttpResponseRedirect(redirection)


@login_required
@permission_required('continuing_education.archive_admission', raise_exception=True)
def archives_procedure(request):
    new_archive_status = True
    return change_archive_status(new_archive_status, request)


def change_archive_status(new_archive_status, request):
    selected_admissions_id = request.POST.getlist("selected_action", default=[])
    for admission_id in selected_admissions_id:
        admission = Admission.objects.get(id=admission_id)
        can_access_admission(request.user, admission)
    redirection = request.META.get('HTTP_REFERER')
    if selected_admissions_id:
        _mark_folders_as_archived(request, selected_admissions_id, new_archive_status)
        return redirect(reverse('archive'))
    else:
        _set_error_message(request)
        return HttpResponseRedirect(redirection)


def _mark_folders_as_archived(request, selected_admissions_id, new_archive_status):
    for admission_id in selected_admissions_id:
        _mark_as_archived(request.user, admission_id, new_archive_status)
    _set_success_message(request, len(selected_admissions_id) > 1, new_archive_status)


def _set_success_message(request, is_plural, admission_archived=True):
    success_msg = "{} {}".format(
        _('Files are now') if is_plural else _('File is now'),
        _('archived') if admission_archived else _('unarchived')
    )
    display_success_messages(request, success_msg)


def _mark_as_archived(user, admission_id, archive_state=True):
    admission = get_object_or_404(Admission, pk=admission_id)
    _set_archived_state(user, admission, archive_state)


def _set_archived_state(user, admission, archived_state):
    if admission:
        admission.archived = archived_state
        save_and_create_revision(
            get_revision_messages(FILE_ARCHIVED) if admission.archived else get_revision_messages(FILE_UNARCHIVED),
            admission, user
        )


def _set_error_message(request):
    error_msg = _('Please select at least one file to archive')
    display_error_messages(request, error_msg)


def _switch_archived_state(user, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    _set_archived_state(user, admission, not admission.archived)
    return admission


@login_required
@permission_required('continuing_education.archive_admission', raise_exception=True)
def unarchives_procedure(request):
    return change_archive_status(False, request)
