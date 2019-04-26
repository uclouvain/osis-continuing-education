from django.db import models
from django.utils.translation import ugettext_lazy as _

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AddressAdmin(SerializableModelAdmin):
    list_display = ('location', 'postal_code', 'city', 'country')


class Address(SerializableModel):
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Location")
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_("Postal code")
    )
    city = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("City")
    )
    country = models.ForeignKey(
        'reference.Country',
        blank=True,
        null=True,
        related_name='address_country',
        verbose_name=_("Country"),
        on_delete=models.CASCADE
    )
