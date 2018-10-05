from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums.enums import YES_NO_CHOICES


class ContinuingEducationPersonForm(ModelForm):
    high_school_diploma = forms.TypedChoiceField(coerce=lambda x: x =='True', required=False,
                                   choices=YES_NO_CHOICES, label=_("high_school_diploma"))

    class Meta:
        model = ContinuingEducationPerson
        fields = [
            'birth_date',
            'birth_location',
            'birth_country',
            'citizenship',
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
