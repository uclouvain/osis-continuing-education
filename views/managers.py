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
from django.contrib.auth.models import Group
from django.shortcuts import render

from base.models.person import Person
from continuing_education.forms.person_training import PersonTrainingForm
from continuing_education.forms.search import ManagerFilterForm
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.person_training import PersonTraining
from continuing_education.views.common import get_object_list, display_errors


@login_required
@permission_required('continuing_education.can_validate_registration', raise_exception=True)
def list_managers(request):
    search_form = ManagerFilterForm(data=request.GET)
    person_training_form = PersonTrainingForm(request.POST or None)
    trainings = ContinuingEducationTraining.objects.all().select_related('education_group')

    if search_form.is_valid():
        managers = search_form.get_managers()
    else:
        managers = Person.objects.filter(
            user__groups__name='continuing_education_training_managers'
        ).order_by('last_name')

    errors = []
    if person_training_form.is_valid():
        person = person_training_form.cleaned_data['person']
        _append_user_to_training_managers(person.user)
        person_training_form.save()
    else:
        errors.append(person_training_form.errors)
        display_errors(request, errors)

    for manager in managers:
        manager.trainings = trainings.filter(
            managers=manager
        ).order_by('education_group__educationgroupyear__acronym').distinct()

    return render(request, "managers.html", {
        'managers': get_object_list(request, managers),
        'search_form': search_form,
        'person_training_form': person_training_form
    })


def _append_user_to_training_managers(user):
    group = Group.objects.get(name='continuing_education_training_managers')
    if user and not user.groups.filter(name=group.name).exists():
        group.user_set.add(user)
