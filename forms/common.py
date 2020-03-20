from django import forms
from django.utils.translation import gettext_lazy as _


def set_participant_required_fields(fields, list_required_fields_for_participant, required=False):
    for field in list_required_fields_for_participant:
        fields[field].widget.attrs['class'] = 'participant_required'
        fields[field].widget.attrs['title'] = _('Field required while participant fills out the form')
        if required:
            fields[field].required = True


class CountryChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, *args, **kwargs):
        super().__init__(queryset, *args, **kwargs)
        self.widget.attrs['style'] = 'text-transform: uppercase;'
