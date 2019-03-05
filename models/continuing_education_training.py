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
import uuid as uuid
from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

from base.models.enums.education_group_types import TrainingType
from base.models.person import Person

CONTINUING_EDUCATION_TRAINING_TYPES = [
    TrainingType.AGGREGATION.name,
    TrainingType.CERTIFICATE.name,
    TrainingType.CERTIFICATE_OF_PARTICIPATION.name,
    TrainingType.CERTIFICATE_OF_SUCCESS.name,
    TrainingType.UNIVERSITY_FIRST_CYCLE_CERTIFICATE.name,
    TrainingType.UNIVERSITY_SECOND_CYCLE_CERTIFICATE.name,
]


class ContinuingEducationTrainingAdmin(ModelAdmin):
    list_display = ('education_group', 'active',)
    search_fields = ['acronym']
    list_filter = ('active',)
    raw_id_fields = ('education_group',)


class ContinuingEducationTraining(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    education_group = models.OneToOneField(
        'base.EducationGroup',
        on_delete=models.CASCADE,
        default=None
    )

    active = models.BooleanField(
        default=False,
        verbose_name=_("Active")
    )

    managers = models.ManyToManyField(Person, through='PersonTraining')

    def get_most_recent_education_group_year(self):
        return self.education_group.educationgroupyear_set.filter(
            education_group_id=self.education_group.pk
        ).latest('academic_year__year')

    def __str__(self):
        education_group_year = self.get_most_recent_education_group_year()
        return "{} - {}".format(education_group_year.acronym, education_group_year.title)
