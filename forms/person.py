from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from base.models.person import Person
from continuing_education.business.admission import disable_existing_fields


def _capitalize_choices(choices):
    return ((choice[0], choice[1].capitalize()) for choice in choices)


class PersonForm(ModelForm):
    first_name = forms.CharField(
        required=True,
        label=_("First name")
    )

    last_name = forms.CharField(
        required=True,
        label=_("Last name")
    )

    gender = forms.ChoiceField(
        choices=_capitalize_choices(Person.GENDER_CHOICES),
        required=True,
        label=_("Gender")
    )

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            disable_existing_fields(self)

    class Meta:
        model = Person

        fields = [
            'first_name',
            'last_name',
            'email',
            'gender'
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}
