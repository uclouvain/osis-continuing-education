import unicodedata

from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from continuing_education.forms.common import CountryChoiceField
from continuing_education.forms.common import set_participant_required_fields
from continuing_education.models.address import Address
from reference.models.country import Country
from reference.models.zipcode import ZipCode

ADDRESS_PARTICIPANT_REQUIRED_FIELDS = ['location', 'postal_code', 'city', 'country', ]
BELGIUM_ISO_CODE = "BE"


class AddressForm(ModelForm):

    location = forms.CharField(
        max_length=50,
        required=False,
    )
    postal_code = forms.CharField(
        max_length=12,
        required=False,
    )
    city = forms.CharField(
        max_length=40,
        required=False,
    )

    country = CountryChoiceField(
        queryset=Country.objects.all(),
        label=_("Country"),
        required=False,
    )

    class Meta:
        model = Address
        fields = [
            'location',
            'postal_code',
            'city',
            'country'
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}

    def __init__(self, data, user=None, **kwargs):
        super().__init__(data, **kwargs)
        set_participant_required_fields(
            self.fields,
            ADDRESS_PARTICIPANT_REQUIRED_FIELDS
        )

    def clean(self):

        cleaned_data = super().clean()
        if cleaned_data.get('country') and cleaned_data.get('country').iso_code == BELGIUM_ISO_CODE:
            if cleaned_data.get('postal_code') and cleaned_data.get('city'):
                cities = ZipCode.objects.filter(country__iso_code=BELGIUM_ISO_CODE, zip_code=cleaned_data.get('postal_code')).order_by('municipality')
                if cities:
                    if not are_postal_code_and_city_compatible(cities, cleaned_data.get('city').lower()):
                        self.add_error('postal_code',
                                       _('Cities available for this belgian postal code %(postal_code)s are : '
                                         '%(possible_cities)s') % {
                                           'postal_code': str(cleaned_data.get('postal_code')),
                                           'possible_cities': ', '.join(city.municipality for city in cities),
                                       })

                else:
                    self.add_error('postal_code',
                                   _('This postal code (%(postal_code)s) is not a belgian one!') % {
                                       'postal_code': str(cleaned_data.get('postal_code'))
                                   }
                                   )
        return cleaned_data


def are_postal_code_and_city_compatible(cities, city_encoded) -> bool:
    for city in cities:
        city_name = city.municipality.lower()
        if city_name == city_encoded or \
                unicodedata.normalize('NFKD', city_name).encode('ascii', 'ignore') == \
                unicodedata.normalize('NFKD', city_encoded).encode('ascii', 'ignore'):
            return True
    return False
