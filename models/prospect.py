##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


class ProspectAdmin(ModelAdmin):
    list_display = ('first_name', 'name', 'email', 'postal_code', 'formation')
    search_fields = ['first_name', 'name', 'email', 'postal_code',
                     'formation__education_group__educationgroupyear__acronym']
    raw_id_fields = ('formation',)


class Prospect(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('Name')
    )
    first_name = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('First name')
    )
    postal_code = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_('Postal code')
    )
    city = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('City')
    )
    email = models.EmailField(
        max_length=255,
        verbose_name=_("Email")
    )
    phone_number = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Phone number")
    )
    formation = models.ForeignKey(
        'continuing_education.ContinuingEducationTraining',
        on_delete=models.PROTECT,
        verbose_name=_("Formation")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name=_("Creation date")
    )

    class Meta:
        default_permissions = ['view']
        permissions = (
            ("export_prospect", "Export a prospect into XLSX file"),
        )

    def __str__(self):
        return "{} - {} {}".format(self.id, self.first_name, self.name)
