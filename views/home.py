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
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from continuing_education.auth.roles.continuing_education_manager import is_continuing_education_manager
from continuing_education.auth.roles.continuing_education_student_worker import is_continuing_education_student_worker
from continuing_education.auth.roles.continuing_education_training_manager import \
    is_continuing_education_training_manager


def can_access_continuing_education(f):
    @wraps(f)
    def inner(request, *args, **kwargs):
        if not request.user.has_module_perms('continuing_education'):
            raise PermissionDenied()
        return f(request, *args, **kwargs)
    return inner


@login_required
@can_access_continuing_education
def main_view(request):
    continuing_education_manager = is_continuing_education_manager(request.user)
    user_is_continuing_education_student_worker = is_continuing_education_student_worker(request.user)
    return render(request, "admin_home.html", {
        'continuing_education_manager': continuing_education_manager,
        'user_is_continuing_education_student_worker': user_is_continuing_education_student_worker,
        'continuing_education_training_manager': is_continuing_education_training_manager(request.user)
    })
