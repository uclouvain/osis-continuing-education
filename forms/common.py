from django.utils.translation import ugettext_lazy as _


def set_participant_required_fields(fields, list_required_fields_for_participant):
    for field in list_required_fields_for_participant:
        fields[field].widget.attrs['class'] = 'participant_required'
        fields[field].widget.attrs['title'] = _('Field required while participant fills out the form')
