from django.utils.translation import ugettext_lazy as _
from django import forms


def set_participant_required_fields(fields, list_required_fields_for_participant):
    for field in list_required_fields_for_participant:
        fields[field].widget.attrs['class'] = 'participant_required'
        fields[field].widget.attrs['title'] = _('Field required while participant fills out the form')


class CountryChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, *args, **kwargs):

        super().__init__(queryset, *args, **kwargs)
        self.widget.attrs['style'] = 'text-transform: uppercase;'
