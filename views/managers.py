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
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import permission_required

from base.models.person import Person
from base.utils.cache import cache_filter
from base.views.common import display_success_messages
from continuing_education.auth.roles.continuing_education_training_manager import ContinuingEducationTrainingManager
from continuing_education.forms.person_training import PersonTrainingForm
from continuing_education.forms.search import ManagerFilterForm
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.enums.groups import TRAINING_MANAGERS_GROUP
from continuing_education.views.common import get_object_list, display_errors


@login_required
@cache_filter()
@permission_required('continuing_education.view_continuingeducationtrainingmanager', raise_exception=True)
def list_managers(request):
    search_form = ManagerFilterForm(data=request.GET)
    trainings = ContinuingEducationTraining.objects.all().select_related('education_group')
    person_training_form = PersonTrainingForm()

    if search_form.is_valid():
        managers = search_form.get_managers()
    else:
        managers = Person.objects.filter(
            user__groups__name=TRAINING_MANAGERS_GROUP
        ).order_by('last_name')

    for manager in managers:
        manager.trainings = trainings.filter(managers=manager).distinct()

    return render(request, "managers.html", {
        'managers': get_object_list(request, managers),
        'search_form': search_form,
        'person_training_form': person_training_form
    })


@login_required
@permission_required('continuing_education.add_continuingeducationtrainingmanager', raise_exception=True)
def add_continuing_education_training_manager(request):
    errors = []
    person_training_form = PersonTrainingForm(request.POST or None)
    if person_training_form.is_valid():
        person = person_training_form.cleaned_data['person']
        _append_user_to_training_managers(person.user)
        person_training_form.save()
        success_msg = _('Successfully assigned %(manager)s to the training %(training)s') % {
            "manager": person,
            "training": person_training_form.cleaned_data['training'].acronym
        }
        display_success_messages(request, success_msg)
    else:
        errors.append(person_training_form.errors)
        display_errors(request, errors)
    return redirect(list_managers)


@login_required
@permission_required('continuing_education.delete_continuingeducationtrainingmanager', raise_exception=True)
def delete_continuing_education_training_manager(request, training, manager):
    redirect_url = request.META.get('HTTP_REFERER', reverse('list_managers'))

    person_training = get_object_or_404(
        ContinuingEducationTrainingManager.objects.select_related('person', 'training'),
        training=training, person=manager
    )
    success_msg = _('Successfully desassigned %(manager)s from the training %(training)s') % {
        "manager": person_training.person,
        "training": person_training.training.acronym
    }
    display_success_messages(request, success_msg)
    person_training.delete()

    return redirect(redirect_url)


def _append_user_to_training_managers(user):
    group = Group.objects.get(name=TRAINING_MANAGERS_GROUP)
    if user and not user.groups.filter(name=group.name).exists():
        group.user_set.add(user)
