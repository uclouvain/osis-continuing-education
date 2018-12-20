from django import forms
from django.forms import ModelForm, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from reference.models.country import Country


class ContinuingEducationPersonForm(ModelForm):
    birth_country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by('name'),
        label=_("Birth country"),
        required=False,
    )

    def __init__(self, *args, **kwargs):

        super(ContinuingEducationPersonForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            self._disable_existing_person_fields()

    def _disable_existing_person_fields(self):
        fields_to_disable = ["birth_country", "birth_date"]

        for field in self.fields.keys():
            self.fields[field].initial = getattr(self.instance, field)
            self.fields[field].widget.attrs['readonly'] = True
            if field in fields_to_disable:
                self.fields[field].widget.attrs['disabled'] = True

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
            continuing_education_person.birth_location or _("Unknown birth place"),
        )
