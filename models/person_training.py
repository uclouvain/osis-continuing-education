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
import uuid as uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model


class PersonTrainingAdmin(ModelAdmin):
    list_display = ('person', 'training',)
    search_fields = ['person__first_name', 'person__last_name']
    raw_id_fields = ('person', 'training',)


class PersonTraining(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.ForeignKey(
        'base.Person',
        on_delete=models.CASCADE
    )

    training = models.ForeignKey(
        'continuing_education.ContinuingEducationTraining',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("person", "training")
        default_permissions = ['view', 'add', 'delete']
