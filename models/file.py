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
import uuid
from pathlib import Path

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.text import get_valid_filename
from django.utils.translation import gettext_lazy as _, pgettext

from backoffice.settings.base import MAX_UPLOAD_SIZE
from continuing_education.models.enums import file_category_choices
from continuing_education.models.enums.admission_state_choices import ACCEPTED
from continuing_education.models.exceptions import TooLongFilenameException, InvalidFileCategoryException, \
    UnallowedFileExtensionException, TooLargeFileSizeException, TooManyFilesException

MAX_ADMISSION_FILES_COUNT = 10
MAX_ADMISSION_FILE_NAME_LENGTH = 100
ALLOWED_EXTENSIONS = [
    'bmp', 'gif', 'jpeg', 'jpg', 'tex', 'xls', 'xlsx', 'doc', 'docx', 'odt', 'txt', 'pdf', 'png', 'pptx', 'ppt', 'rtf'
]


def admission_directory_path(instance, filename):
    return 'continuing_education/admission_{}/{}'.format(
        instance.admission.id,
        instance.uuid
    )


class AdmissionFileAdmin(ModelAdmin):
    list_display = ('admission', 'name', 'file_category', 'path', 'uploaded_by')
    raw_id_fields = ('uploaded_by',)


class AdmissionFile(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    admission = models.ForeignKey(
        'continuing_education.Admission',
        blank=True,
        null=True,
        verbose_name=pgettext("continuing_education", "Admission"),
        on_delete=models.CASCADE
    )

    name = models.CharField(
        max_length=MAX_ADMISSION_FILE_NAME_LENGTH,
        verbose_name=_("Name")
    )

    path = models.FileField(
        upload_to=admission_directory_path,
        verbose_name=_("Path"),
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
        choices=file_category_choices.FILE_CATEGORY_CHOICES,
        default=file_category_choices.DOCUMENT,
        max_length=20
    )

    class Meta:
        default_permissions = []

    def save(self, *args, **kwargs):
        if not (self.size and self.name):
            self.size = self.path.size
            self.name = get_valid_filename(self.path.name)
        self._validate_file()
        super(AdmissionFile, self).save(*args, **kwargs)

    def _validate_file(self):
        self._validate_admission_files_count()
        self._validate_file_name_length()
        self._validate_invoice_status()
        self._validate_extension()
        self._validate_file_size()

    def _validate_admission_files_count(self):
        if AdmissionFile.objects.filter(admission=self.admission).count() >= MAX_ADMISSION_FILES_COUNT:
            raise TooManyFilesException(max_count=MAX_ADMISSION_FILES_COUNT)

    def _validate_file_size(self):
        if self.size > MAX_UPLOAD_SIZE:
            raise TooLargeFileSizeException(size=self.size, max_size=MAX_UPLOAD_SIZE)

    def _validate_extension(self):
        file_extension = Path(self.path.name).suffix[1:].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise UnallowedFileExtensionException(extension=file_extension, allowed_extensions=ALLOWED_EXTENSIONS)

    def _validate_invoice_status(self):
        if self.admission.state != ACCEPTED and self.file_category == file_category_choices.INVOICE:
            raise InvalidFileCategoryException()

    def _validate_file_name_length(self):
        if len(self.name) > MAX_ADMISSION_FILE_NAME_LENGTH:
            raise TooLongFilenameException(max_length=MAX_ADMISSION_FILE_NAME_LENGTH)
