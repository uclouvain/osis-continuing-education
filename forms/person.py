from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models.person import Person
from continuing_education.business.admission import disable_existing_fields


class PersonForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

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
