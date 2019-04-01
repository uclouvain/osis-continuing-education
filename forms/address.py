from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from continuing_education.forms.common import set_participant_required_fields
from continuing_education.models.address import Address
from reference.models.country import Country

ADDRESS_PARTICIPANT_REQUIRED_FIELDS = ['location', 'postal_code', 'city', 'country', ]


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

    def __init__(self, data, user=None, **kwargs):
        super().__init__(data, **kwargs)
        set_participant_required_fields(self.fields,
                                        ADDRESS_PARTICIPANT_REQUIRED_FIELDS
                                        )
