from django.forms import ModelForm

from base.forms.bootstrap import BootstrapModelForm
from continuing_education.models.admission import Admission
from django.utils.translation import ugettext_lazy as _
from django import forms

class AdmissionForm(ModelForm):
    high_school_diploma = forms.TypedChoiceField(coerce=lambda x: x =='True',
                                   choices=((False, _('No')), (True, _('Yes'))))

    class Meta:
        model = Admission
        fields = [
            'first_name',
            'last_name',
            'birth_date',
            'birth_location',
            'birth_country',
            'citizenship',
            'gender',
            # Contact
            'phone_mobile',
            'email',
            # Address
            'location',
            'postal_code',
            'city',
            'country',
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
            # Motivation
            'motivation',
            'professional_impact',
            # Formation
            'formation_title',
            'courses_formula',
            'program_code',
            'faculty',
            'formation_administrator',
            # Awareness
            'ucl_website',
            'formation_website',
            'press',
            'facebook',
            'linkedin',
            'customized_mail',
            'emailing',
            # State
            'state',
        ]