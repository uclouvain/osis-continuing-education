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
from django.shortcuts import render

from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices


@login_required
@permission_required('continuing_education.can_access_admission', raise_exception=True)
def list_tasks(request):
    all_admissions = Admission.objects.select_related(
        'person_information__person', 'formation__academic_year'
    ).order_by(
        'person_information__person__last_name', 'person_information__person__first_name'
    )

    registrations_to_validate = all_admissions.filter(
        state=admission_state_choices.REGISTRATION_SUBMITTED
    )

    admissions_diploma_to_produce = all_admissions.filter(
        state=admission_state_choices.VALIDATED,
        diploma_produced=False
    )

    return render(request, "tasks.html", {
        'registrations_to_validate': registrations_to_validate,
        'admissions_diploma_to_produce': admissions_diploma_to_produce,
    })
