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

from django.utils.translation import gettext_lazy as _
from rest_framework import permissions

from continuing_education.models.enums.admission_state_choices import ACCEPTED, DRAFT


class HasAdmissionAccess(permissions.BasePermission):
    message = _('Getting this admission not allowed.')

    def has_object_permission(self, request, view, obj):
        return obj.person_information.person.user == request.user


class CanSubmit(permissions.BasePermission):
    message = _(
        'To submit a registration, its state must be ACCEPTED. To submit an admission, its state must be DRAFT.'
    )

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.state == ACCEPTED or (obj.state == DRAFT and not obj.formation.registration_required)
        return True


class CanSubmitAdmission(permissions.BasePermission):
    message = _('To submit an admission, its state must be DRAFT.')

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.state == DRAFT
        return True


class CanSendFiles(permissions.BasePermission):
    message = _('Uploading and deleting files is not allowed if admission is not editable.')

    def has_object_permission(self, request, view, obj):
        if request.method not in permissions.SAFE_METHODS:
            return obj.admission.state in [ACCEPTED, DRAFT]
        return True
