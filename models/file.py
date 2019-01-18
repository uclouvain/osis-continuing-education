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
import uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.enums import file_category_choices
from continuing_education.models.exceptions import TooLongFilenameException

MAX_ADMISSION_FILE_NAME_LENGTH = 100


def admission_directory_path(instance, filename):
    return 'continuing_education/admission_{}/{}'.format(
        instance.admission.id,
        filename
    )


class FileAdmin(ModelAdmin):
    list_display = ('admission', 'name', 'path', 'uploaded_by')
    raw_id_fields = ('uploaded_by',)


class File(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    admission = models.ForeignKey(
        'continuing_education.Admission',
        blank=True,
        null=True,
        verbose_name=_("Admission")
    )

    name = models.CharField(
        max_length=MAX_ADMISSION_FILE_NAME_LENGTH,
        verbose_name=_("Name")
    )

    path = models.FileField(
        upload_to=admission_directory_path,
        verbose_name=_("Path")
    )

    size = models.IntegerField(
        null=True,
        verbose_name=_("Size")
    )

    created_date = models.DateTimeField(auto_now_add=True, editable=False)

    uploaded_by = models.ForeignKey(
        'base.person',
        null=True,
        verbose_name=_("Uploaded by"),
        on_delete=models.PROTECT
    )

    file_category = models.CharField(
        choices=file_category_choices.FILE_TYPE_CATEGORIES,
        default=file_category_choices.DOCUMENT,
        max_length=20
    )

    def save(self, *args, **kwargs):
        if len(self.name) > MAX_ADMISSION_FILE_NAME_LENGTH:
            raise TooLongFilenameException(
                _("The name of the file is too long : maximum %(length)s characters.") % {
                    'length': MAX_ADMISSION_FILE_NAME_LENGTH
                }
            )
        super(File, self).save(*args, **kwargs)
