from django import forms
from django.forms import ModelForm, ChoiceField
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices, enums
from reference.models.country import Country


class TitleChoiceField(forms.ModelChoiceField):
    def label_from_instance(obj):
        return "{} - {}".format(obj.acronym, obj.title)


class AdmissionForm(ModelForm):
    state = ChoiceField(choices=admission_state_choices.STATE_CHOICES, required=False)
    citizenship = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by('name'),
        label=_("citizenship"),
        required=False,
    )
    high_school_diploma = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=enums.YES_NO_CHOICES,
        label=_("high_school_diploma")
    )

    class Meta:
        model = Admission
        fields = [
            'formation',

            # Contact
            'person_information',
            'citizenship',
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

            # Motivation
            'motivation',
            'professional_impact',

            # Awareness
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',

            # State
            'state',
        ]
