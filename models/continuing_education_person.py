import datetime
import uuid as uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _


class ContinuingEducationPersonAdmin(ModelAdmin):
    list_display = ('person', 'birth_date',)
    search_fields = ['person__first_name', 'person__last_name']
    list_filter = ('birth_country',)


class ContinuingEducationPerson(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person = models.OneToOneField(
        'base.Person',
        on_delete=models.CASCADE
    )

    birth_date = models.DateField(
        blank=True,
        default=datetime.date(2000, 1, 1),
        verbose_name=_("Birth date")
    )

    birth_location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Birth location")
    )
    birth_country = models.ForeignKey(
        'reference.Country',
        blank=True,
        null=True,
        related_name='birth_country',
        verbose_name=_("Birth country"),
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{} - {} {}".format(self.id, self.person.first_name, self.person.last_name)


def find_by_person(person):
    return ContinuingEducationPerson.objects.filter(person=person).first()
