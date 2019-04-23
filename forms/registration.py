from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.admission import Admission
from continuing_education.models.enums.enums import YES_NO_CHOICES


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
        ]
