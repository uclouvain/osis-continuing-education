from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models.person import Person
from continuing_education.forms.common import set_participant_required_fields

ADMISSION_PARTICIPANT_REQUIRED_FIELDS = [
    'first_name', 'last_name', 'gender',
]


class PersonForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

        set_participant_required_fields(self.fields,
                                        ADMISSION_PARTICIPANT_REQUIRED_FIELDS,
                                        True)

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
