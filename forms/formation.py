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
            'additional_information_label',
            'registration_required',
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}

    def __init__(self, data, user=None, **kwargs):
        super().__init__(data=data, **kwargs)
        self.fields['additional_information_label'].widget.attrs['placeholder'] = _(
            "Describe here additional information that will be asked to the participant:\n"
            "- as a list of question(s) - maximum 1 sentence by question \n"
            "- numbered 1., 2., 3.,... if multiple questions \n\n"
            "This text will appear the same on the participant's admission form\n\n"
            "Example: \n"
            "1. What is your pedagogical title ? \n"
            "2. ..."
        )
        if user and not user.has_perm('continuing_education.set_training_active'):
            self.fields['active'].disabled = True
