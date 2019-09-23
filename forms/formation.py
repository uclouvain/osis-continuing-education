from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from continuing_education.models.continuing_education_training import ContinuingEducationTraining


class ContinuingEducationTrainingForm(ModelForm):

    class Meta:
        model = ContinuingEducationTraining
        fields = [
            'training_aid',
            'active',
            'postal_address',
            'additional_information_label'
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}

    def __init__(self, data, user=None, **kwargs):
        super().__init__(data=data, **kwargs)
        if user and not user.groups.filter(name='continuing_education_managers').exists():
            self.fields['training_aid'].disabled = True
            self.fields['active'].disabled = True
