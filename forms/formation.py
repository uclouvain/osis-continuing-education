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
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}
