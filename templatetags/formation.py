##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from continuing_education.models.admission import get_formation_display
from continuing_education.models.continuing_education_training import ContinuingEducationTraining

register = template.Library()


@register.filter
def get_formation_denomination(formation):
    return get_formation_display(formation.partial_acronym, formation.acronym, formation.academic_year)


@register.filter
def get_formation_faculty(formation):
    most_recent_education_group = formation.educationgroupyear_set.filter(education_group_id=formation.id) \
        .latest('academic_year__year')
    return get_management_faculty(most_recent_education_group)


@register.filter
def get_formation_title(formation):
    most_recent_education_group = formation.educationgroupyear_set.filter(education_group_id=formation.id) \
        .latest('academic_year__year')
    return most_recent_education_group.title


@register.filter
def get_active_continuing_education_formation(formation):
    continuing_education_training = ContinuingEducationTraining.objects.filter(
        education_group=formation
    ).first()
    if continuing_education_training:
        return _('Active') if continuing_education_training.active else _('Inactive')
    return _('Not organized')
