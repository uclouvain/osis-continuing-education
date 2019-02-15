from datetime import datetime

from django import forms
from django.forms import ModelForm, ChoiceField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from continuing_education.business.enums.rejected_reason import REJECTED_REASON_CHOICES, OTHER
from continuing_education.business.enums.waiting_reason import WAITING_REASON_CHOICES
from continuing_education.forms.account import ContinuingEducationPersonChoiceField
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums import admission_state_choices
from continuing_education.models.enums import enums
from reference.models.country import Country
from base.models.entity_version import search
from django.utils.translation import ugettext_lazy as _, pgettext
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, VALIDATED, \
    REGISTRATION_SUBMITTED
from base.models.entity_version import EntityVersion
from base.models import entity_version
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type

STATE_TO_DISPLAY = [SUBMITTED, REJECTED, WAITING]


class BootstrapForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(BootstrapForm, self).__init__(*args, **kwargs)
        set_form_control(self)


def set_form_control(self):
    for field in self.fields:
        attr_class = self.fields[field].widget.attrs.get('class') or ''
        self.fields[field].widget.attrs['class'] = attr_class + ' form-control'


class FacultyModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.acronym


class FormationModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "{}{} - {}".format(
            " - " if obj.partial_acronym else '',
            obj.acronym,
            obj.academic_year,
        )


class AdmissionFilterForm(BootstrapForm):
    faculty = FacultyModelChoiceField(
        queryset=
        entity_version.find_latest_version(datetime.now()).filter(entity_type=entity_type.FACULTY).order_by('acronym'),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False
    )

    formation = FormationModelChoiceField(
        queryset=None,
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(AdmissionFilterForm, self).__init__(*args, **kwargs)
        field = self.fields['formation']
        field.queryset = EducationGroupYear.objects\
            .filter(id__in=Admission.objects.filter(state__in=STATE_TO_DISPLAY)
                    .values_list('formation', flat=False).distinct('formation')
                    ).order_by('acronym')

    def get_admissions(self):
        faculty = self.cleaned_data['faculty']
        formation = self.cleaned_data.get('formation')

        qs = Admission.objects.filter(
            state__in=STATE_TO_DISPLAY
        ).order_by('person_information')

        if faculty:
            formations = _get_formations_by_faculty(faculty)
            qs = qs.filter(
                formation__acronym__in=formations
            ).order_by('person_information')

        if formation:
            qs = qs.filter(formation=formation)

        return qs


def _get_formations_by_faculty(faculty):
    entity = EntityVersion.objects.filter(id=faculty.id).first().entity
    entities_child = EntityVersion.objects.filter(parent=entity)
    formations = EducationGroupYear.objects.filter(
        management_entity=entity
    )
    for child in entities_child:
        formations |= EducationGroupYear.objects.filter(
            management_entity=child.entity
        )
    formations = [formation.acronym for formation in formations]
    return formations

