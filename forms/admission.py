from django import forms
from django.core.validators import RegexValidator
from django.forms import ModelForm, ChoiceField
from django.utils.translation import gettext_lazy as _

from continuing_education.business.enums.rejected_reason import REJECTED_REASON_CHOICES, OTHER
from continuing_education.business.enums.waiting_reason import WAITING_REASON_CHOICES, \
    WAITING_REASON_CHOICES_SHORTENED_DISPLAY
from continuing_education.forms.account import ContinuingEducationPersonChoiceField
from continuing_education.forms.common import CountryChoiceField
from continuing_education.forms.common import set_participant_required_fields
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums import enums
from reference.models.country import Country

ADMISSION_PARTICIPANT_REQUIRED_FIELDS = [
    'citizenship', 'phone_mobile', 'high_school_diploma', 'last_degree_level',
    'last_degree_field', 'last_degree_institution', 'last_degree_graduation_year',
    'professional_status', 'current_occupation', 'current_employer', 'activity_sector', 'motivation',
    'professional_personal_interests', 'formation',
]

phone_regex = RegexValidator(
    regex=r'^(?P<prefix_intro>\+|0{1,2})\d{7,15}$',
    message=_("Phone number must start with 0 or 00 or '+' followed by at least 7 digits and up to 15 digits.")
)


class AdmissionForm(ModelForm):
    phone_mobile = forms.CharField(
        validators=[phone_regex],
        required=False,
        label=_("Phone mobile"),
        widget=forms.TextInput(attrs={'placeholder': '0474123456 - 0032474123456 - +32474123456'})
    )
    formation = forms.ModelChoiceField(
        queryset=ContinuingEducationTraining.objects.all().select_related('education_group')
    )
    state = ChoiceField(
        choices=admission_state_choices.STATE_CHOICES,
        required=False
    )
    citizenship = CountryChoiceField(
        queryset=Country.objects.all().order_by('name'),
        label=_("Citizenship"),
        required=False,
    )

    high_school_diploma = forms.TypedChoiceField(
        coerce=lambda x: x == 'True',
        required=False,
        choices=enums.YES_NO_CHOICES,
        label=_("High school diploma")
    )
    person_information = ContinuingEducationPersonChoiceField(
        queryset=ContinuingEducationPerson.objects.all().order_by(
            'person__last_name', 'person__first_name'
        ).select_related('person'),
        required=False,
        empty_label=_("New person")
    )

    def clean_phone_mobile(self):
        return self.cleaned_data['phone_mobile'].replace(' ', '')

    def __init__(self, data, user=None, **kwargs):
        super().__init__(data, **kwargs)
        qs = self.fields['formation'].queryset
        if user and not user.groups.filter(name='continuing_education_managers').exists():
            qs = qs.filter(
                managers=user.person
            )
        self.fields['formation'].queryset = qs.order_by(
            'education_group__educationgroupyear__acronym'
        ).distinct()

        set_participant_required_fields(self.fields,
                                        ADMISSION_PARTICIPANT_REQUIRED_FIELDS)

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
            'professional_personal_interests',

            # Awareness
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_word_of_mouth',
            'awareness_friends',
            'awareness_former_students',
            'awareness_moocs',
            'awareness_other',

            # State
            'state',
            'state_reason',

            # Additional Information
            'additional_information'
        ]


class RejectedAdmissionForm(ModelForm):

    rejected_reason = forms.ChoiceField(
        choices=REJECTED_REASON_CHOICES,
        required=True,
        label=_('Predefined reason'),
    )
    other_reason = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label=_('Other rejection reason'),
    )

    class Meta:
        model = Admission
        fields = [
            'state',
            'state_reason',
        ]

    def __init__(self, data, **kwargs):

        super().__init__(data, **kwargs)

        if data is None:
            # GET
            if self.instance.state == admission_state_choices.REJECTED:
                self._reject_state_init()
            else:
                self._disabled_and_init_other_reason()

    def _reject_state_init(self):
        if any(self.instance.state_reason in reason for reason in REJECTED_REASON_CHOICES):
            self.fields['rejected_reason'].initial = self.instance.state_reason
            self._disabled_and_init_other_reason()
        elif self.instance.state_reason:
            self.fields['rejected_reason'].initial = OTHER
            self.fields['other_reason'].disabled = False
            self.fields['other_reason'].initial = self.instance.state_reason

    def _disabled_and_init_other_reason(self):
        self.fields['other_reason'].disabled = True
        self.fields['other_reason'].initial = ''

    def save(self):
        instance = super().save(commit=False)
        if self.cleaned_data["rejected_reason"] == OTHER:
            instance.state_reason = self.cleaned_data["other_reason"]
        else:
            instance.state_reason = self.cleaned_data["rejected_reason"]
        instance.save()
        return instance


class WaitingAdmissionForm(ModelForm):

    waiting_reason = forms.ChoiceField(
        choices=WAITING_REASON_CHOICES_SHORTENED_DISPLAY,
        required=True,
        label=_('Predefined reason'),
    )
    other_reason = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label=_('Other waiting reason'),
    )

    class Meta:
        model = Admission
        fields = [
            'state',
            'state_reason',
        ]

    def __init__(self, data, **kwargs):

        super().__init__(data, **kwargs)

        if data is None:
            # GET
            if self.instance.state == admission_state_choices.WAITING:
                self._waiting_state_init()
            else:
                self._disabled_and_init_other_reason()

    def _waiting_state_init(self):
        if any(self.instance.state_reason in reason for reason in WAITING_REASON_CHOICES):
            self.fields['waiting_reason'].initial = self.instance.state_reason
            self._disabled_and_init_other_reason()
        elif self.instance.state_reason:
            self.fields['waiting_reason'].initial = OTHER
            self.fields['other_reason'].disabled = False
            self.fields['other_reason'].initial = self.instance.state_reason

    def _disabled_and_init_other_reason(self):
        self.fields['other_reason'].disabled = True
        self.fields['other_reason'].initial = ''

    def save(self):
        instance = super().save(commit=False)
        if self.cleaned_data["waiting_reason"] == OTHER:
            instance.state_reason = self.cleaned_data["other_reason"]
        else:
            instance.state_reason = self.cleaned_data["waiting_reason"]
        instance.save()
        return instance


class ConditionAcceptanceAdmissionForm(ModelForm):

    condition_of_acceptance_existing = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            (True, _("Conditionally")),
            (False, _("Unconditionally"))
        ],
        label=_('Accept the file'),
    )
    condition_of_acceptance = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label=_('Condition of acceptance'),
    )

    class Meta:
        model = Admission
        fields = [
            'state',
            'condition_of_acceptance',
        ]

    def __init__(self, data, **kwargs):

        super().__init__(data, **kwargs)

        if data is None:
            # GET
            if self.instance.state == admission_state_choices.ACCEPTED:
                self._accepted_state_init()
            else:
                self.fields['condition_of_acceptance'].initial = self.instance.condition_of_acceptance
                self.fields['condition_of_acceptance_existing'].initial = False
                self.fields['condition_of_acceptance'].disabled = True

    def _accepted_state_init(self):
        self.fields['condition_of_acceptance'].initial = self.instance.condition_of_acceptance

        if not self.instance.condition_of_acceptance:
            self.fields['condition_of_acceptance_existing'].initial = False
            self.fields['condition_of_acceptance'].disabled = True
        else:
            self.fields['condition_of_acceptance_existing'].initial = True
            self.fields['condition_of_acceptance'].disabled = False

    def save(self):
        instance = super().save(commit=False)

        if eval(self.cleaned_data["condition_of_acceptance_existing"]):
            instance.condition_of_acceptance = self.cleaned_data["condition_of_acceptance"]
        else:
            instance.condition_of_acceptance = ''
        instance.save()
        return instance


class CancelAdmissionForm(ModelForm):

    class Meta:
        model = Admission
        fields = [
            'state',
            'state_reason',
        ]

    def save(self):
        instance = super().save(commit=False)
        instance.condition_of_acceptance = ''
        instance.save()
        return instance
