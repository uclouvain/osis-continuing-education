from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _

def admission_directory_path(instance, filename):
    return 'continuing_education/admission_{0}/{1}'\
        .format(instance.admission.id, filename)

class FileAdmin(ModelAdmin):
    list_display = ('admission', 'name', 'file',)


class File(Model):

    admission = models.ForeignKey(
        'continuing_education.Admission',
        blank=True,
        null=True,
        verbose_name=_("admision")
    )

    name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("file_name")
    )

    file = models.FileField(
        upload_to=admission_directory_path,
    )
