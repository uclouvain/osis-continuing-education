from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from continuing_education.auth.roles.continuing_education_training_manager import \
    is_continuing_education_training_manager
from continuing_education.forms.admission import phone_regex
from continuing_education.models.admission import Admission
from continuing_education.models.enums.enums import YES_NO_CHOICES

UNUPDATABLE_FIELDS_FOR_CONTINUING_EDUCATION_TRAINING_MGR = ['registration_file_received', 'ucl_registration_complete']


class RegistrationForm(ModelForm):
    previous_ucl_registration = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        choices=YES_NO_CHOICES
    )
    use_address_for_billing = forms.ChoiceField(widget=forms.RadioSelect,
                                                choices=[
                                                    (True, _("residence address mentioned earlier")),
                                                    (False, _("an other address"))
                                                ],
                                                label=_('I would like the billing address to be :'),
                                                required=False)

    use_address_for_post = forms.ChoiceField(widget=forms.RadioSelect,
                                             choices=[
                                                 (True, _("residence address mentioned earlier")),
                                                 (False, _("an other address"))
                                             ],
                                             label=_('I would like the post address to be :'),
                                             required=False)
    residence_phone = forms.CharField(
        validators=[phone_regex],
        required=False,
        label=_("Residence phone"),
        widget=forms.TextInput(attrs={'placeholder': '082123456 - 003282123456 - +3282123456'})
    )

    def __init__(self, data, only_billing=False, user=None, **kwargs):
        super().__init__(data, **kwargs)
        if only_billing:
            self.fields['previous_ucl_registration'].required = False

        if user and is_continuing_education_training_manager(user):
            for field_name in UNUPDATABLE_FIELDS_FOR_CONTINUING_EDUCATION_TRAINING_MGR:
                self.fields[field_name].disabled = True

    class Meta:
        model = Admission
        fields = [
            'registration_type',
            'use_address_for_billing',
            'billing_address',
            'head_office_name',
            'company_number',
            'vat_number',
            'national_registry_number',
            'id_card_number',
            'passport_number',
            'marital_status',
            'spouse_name',
            'children_number',
            'previous_ucl_registration',
            'previous_noma',
            'use_address_for_post',
            'residence_address',
            'residence_phone',
            'ucl_registration_complete',
            'noma',
            'payment_complete',
            'formation_spreading',
            'prior_experience_validation',
            'assessment_presented',
            'assessment_succeeded',
            'registration_file_received',
            'diploma_produced',
            'sessions',
            'reduced_rates',
            'spreading_payments',
            'comment'
        ]
