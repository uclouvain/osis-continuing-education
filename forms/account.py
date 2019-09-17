from django.forms import ModelForm, ModelChoiceField
from django.utils.translation import gettext_lazy as _

from continuing_education.forms.common import CountryChoiceField, set_participant_required_fields
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from reference.models.country import Country

ADMISSION_PARTICIPANT_REQUIRED_FIELDS = [
    'birth_date', 'birth_location', 'birth_country'
]


class ContinuingEducationPersonForm(ModelForm):
    birth_country = CountryChoiceField(
        queryset=Country.objects.all().order_by('name'),
        label=_("Birth country"),
        required=False,
    )

    def __init__(self, *args, **kwargs):

        super(ContinuingEducationPersonForm, self).__init__(*args, **kwargs)

        set_participant_required_fields(self.fields,
                                        ADMISSION_PARTICIPANT_REQUIRED_FIELDS,
                                        True)

    class Meta:
        model = ContinuingEducationPerson
        fields = [
            'birth_date',
            'birth_location',
            'birth_country',
        ]


class ContinuingEducationPersonChoiceField(ModelChoiceField):
    def label_from_instance(self, continuing_education_person):
        return "{}, {} ({} / {})".format(
            continuing_education_person.person.last_name,
            continuing_education_person.person.first_name,
            continuing_education_person.birth_date,
            continuing_education_person.birth_location.upper() if continuing_education_person.birth_location
            else _("Unknown birth place"),
        )
