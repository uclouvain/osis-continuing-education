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
from django import template
from django.utils.translation import gettext_lazy as _

from continuing_education.business.admission import get_management_faculty
from continuing_education.models.continuing_education_training import ContinuingEducationTraining

DISABLED = "disabled"

register = template.Library()


@register.filter
def get_active_continuing_education_formation(formation):
    continuing_education_training = ContinuingEducationTraining.objects.filter(
        education_group=formation
    ).first()
    if continuing_education_training:
        return _('Active') if continuing_education_training.active else _('Inactive')
    return _('Not organized')


@register.filter
def get_most_recent_education_group(formation):
    return formation.educationgroupyear_set.filter(education_group_id=formation.id)\
        .select_related('academic_year').latest('academic_year__year')


@register.filter
def get_faculty(most_recent_education_group):
    return get_management_faculty(most_recent_education_group)


@register.simple_tag(takes_context=True)
def action_disabled(context, **kwargs):
    formation = kwargs['formation']

    continuing_education_training_manager = context['continuing_education_training_manager']

    if continuing_education_training_manager:
        trainings_managing = context['trainings_managing']
        if isinstance(formation, ContinuingEducationTraining) and trainings_managing:
            if formation.id not in trainings_managing:
                return DISABLED
        else:
            return DISABLED
    return ""
