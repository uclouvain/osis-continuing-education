from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.address import Address
from reference.models.country import Country


class AddressForm(ModelForm):
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by('name'),
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
