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

from base.models.person import Person
from continuing_education.forms.search import ManagerFilterForm
from continuing_education.models.person_training import PersonTraining
from continuing_education.views.common import get_object_list


@login_required
@permission_required('continuing_education.can_validate_admission', raise_exception=True)
def list_managers(request):
    search_form = ManagerFilterForm(data=request.GET)
    managers = Person.objects.filter(user__groups__name='continuing_education_training_managers')
    if search_form.is_valid():
        managers = search_form.get_managers()
    for manager in managers:
        manager.trainings = []
        person_trainings = PersonTraining.objects.filter(person=manager).select_related(
            'training'
        )
        for affectation in person_trainings:
            manager.trainings.append(affectation.training)

    return render(request, "managers.html", {
        'managers': get_object_list(request, managers),
        'search_form': search_form
    })
