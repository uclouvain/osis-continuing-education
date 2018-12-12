from django import forms
from django.forms import ModelForm, ChoiceField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from continuing_education.forms.account import ContinuingEducationPersonChoiceField
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums import admission_state_choices, enums
from reference.models.country import Country


class FormationChoiceField(ModelChoiceField):
    def label_from_instance(self, formation):
        return "{} {}".format(
            formation.acronym,
            formation.academic_year,
        )


class AdmissionForm(ModelForm):
    state = ChoiceField(
        choices=admission_state_choices.STATE_CHOICES,
        required=False
    )
    citizenship = forms.ModelChoiceField(
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
        queryset=ContinuingEducationPerson.objects.all().order_by('person__last_name', 'person__first_name'),
        required=False,
        empty_label=_("New person")
    )
    formation = FormationChoiceField(
        queryset=EducationGroupYear.objects.filter(
            education_group_type__category=education_group_categories.TRAINING,
            academic_year=current_academic_year().next()
        ).order_by('acronym')
    )

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
            'professional_impact',

            # Awareness
            'awareness_ucl_website',
            'awareness_formation_website',
            'awareness_press',
            'awareness_facebook',
            'awareness_linkedin',
            'awareness_customized_mail',
            'awareness_emailing',
            'awareness_other',

            # State
            'state',
        ]
