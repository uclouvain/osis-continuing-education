from dal import autocomplete
from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from base.models.person import Person
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.person_training import PersonTraining
from reference.models.country import Country


class PersonTrainingForm(ModelForm):

    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=autocomplete.ModelSelect2(url='employee_autocomplete')
    )

    training = forms.ModelChoiceField(
        queryset=ContinuingEducationTraining.objects.filter(active=True).order_by(
            'education_group__educationgroupyear__acronym'
        ).distinct()
    )

    class Meta:
        model = PersonTraining

        fields = [
            'person',
            'training',
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}
