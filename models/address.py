import uuid as uuid

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


class AddressAdmin(ModelAdmin):
    list_display = ('location', 'postal_code', 'city', 'country')


class Address(Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

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
