import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class ContinuingEducationPersonAdmin(SerializableModelAdmin):
    list_display = ('person', 'birth_date',)
    search_fields = ['first_name', 'last_name']
    list_filter = ('birth_country',)


class ContinuingEducationPerson(SerializableModel):
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
        verbose_name=_("Birth country")
    )

    def __str__(self):
        return "{} - {} {}".format(self.id, self.person.first_name, self.person.last_name)


def find_by_person(person):
    return ContinuingEducationPerson.objects.filter(person=person).first()
