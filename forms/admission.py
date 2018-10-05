from django import forms
from django.forms import ModelForm, ChoiceField

from continuing_education.models.admission import Admission

class TitleChoiceField(forms.ModelChoiceField):
    def label_from_instance(obj):
        return "{} - {}".format(obj.acronym, obj.title)

class AdmissionForm(ModelForm):

    class Meta:
        model = Admission
        fields = [
            'formation',
            'person_information',
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
