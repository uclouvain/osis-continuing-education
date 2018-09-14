from django.forms import ModelForm

from base.models import offer_year
from continuing_education.models.admission import Admission
from django.utils.translation import ugettext_lazy as _
from django import forms

class TitleChoiceField(forms.ModelChoiceField):
    def label_from_instance(obj):
        return "{} - {}".format(obj.acronym, obj.title)

class AdmissionForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super(AdmissionForm, self).__init__(*args, **kwargs)
        self.fields['formation'].label_from_instance = TitleChoiceField.label_from_instance
        self.fields['faculty'].label_from_instance = TitleChoiceField.label_from_instance
        # avoid adding META ordering in OfferYear model
        self.fields['formation'].queryset = self.fields['formation'].queryset.all().order_by('acronym')

    class Meta:
        model = Admission
        fields = [
            'person',
            # Motivation
            'motivation',
            'professional_impact',
            # Formation
            'formation',
            'faculty',
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
        #automatic translation of field names
        labels = {field : _(field) for field in fields}