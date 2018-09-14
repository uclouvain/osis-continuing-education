from django.forms import ModelForm

from django.utils.translation import ugettext_lazy as _
from django import forms

from continuing_education.models.person import Person


class PersonForm(ModelForm):
    high_school_diploma = forms.TypedChoiceField(coerce=lambda x: x =='True', required=False,
                                   choices=((False, _('No')), (True, _('Yes'))), label=_("high_school_diploma"))

    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'birth_date',
            'birth_location',
            'birth_country',
            'citizenship',
            'gender',
            # Contact
            'address',
            'phone_mobile',
            'email',
            # Education
            'high_school_diploma',
            'high_school_graduation_year',
            'last_degree_level',
            'last_degree_field',
            'last_degree_institution',
            'last_degree_graduation_year',
            'other_educational_background',
            # Professional Background
            'professional_status',
            'current_occupation',
            'current_employer',
            'activity_sector',
            'past_professional_activities',
        ]
        #automatic translation of field names
        labels = {field : _(field) for field in fields}