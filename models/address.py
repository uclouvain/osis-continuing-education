from django.contrib.admin import ModelAdmin
from django.db import models
from django.forms import model_to_dict


class AddressAdmin(ModelAdmin):
    list_display = ('location', 'postal_code','city','country')

class Address(models.Model):
    location = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='address_country')

    def compare(self, obj):
        fields = [x for x in self.__dict__.keys() if x is not '_state']
        return model_to_dict(self, fields=fields) == model_to_dict(obj, fields=fields)