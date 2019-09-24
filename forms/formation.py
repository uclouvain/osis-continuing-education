from django.forms import ModelForm, CharField, Textarea
from django.utils.translation import gettext_lazy as _

from continuing_education.business.perms import is_continuing_education_manager
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
        self.fields['additional_information_label'].widget.attrs['placeholder'] = _(
            "Please answer the following questions in sequence: \n 1)... \n 2)... \n 3)..."
        )
        if user and not is_continuing_education_manager(user):
            self.fields['training_aid'].disabled = True
            self.fields['active'].disabled = True
