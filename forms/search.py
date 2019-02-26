from datetime import datetime

from django import forms
from django.forms import ModelForm, ChoiceField, ModelChoiceField
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from base.models.academic_year import current_academic_year
from base.models.education_group_year import EducationGroupYear
from base.models.enums import education_group_categories
from continuing_education.business.enums.rejected_reason import REJECTED_REASON_CHOICES, OTHER
from continuing_education.business.enums.waiting_reason import WAITING_REASON_CHOICES
from continuing_education.forms.account import ContinuingEducationPersonChoiceField
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.enums.admission_state_choices import REGISTRATION_STATE_CHOICES
from continuing_education.models.enums import enums
from reference.models.country import Country
from base.models.entity_version import search
from django.utils.translation import ugettext_lazy as _, pgettext
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, DRAFT, VALIDATED, \
    REGISTRATION_SUBMITTED, ACCEPTED, REGISTRATION_SUBMITTED, VALIDATED, STATE_CHOICES, ARCHIVE_STATE_CHOICES
from base.models.entity_version import EntityVersion
from base.models import entity_version
from base.models.education_group_year import EducationGroupYear
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type
from operator import itemgetter
from base.business.entity import get_entities_ids

STATE_TO_DISPLAY = [SUBMITTED, REJECTED, WAITING]
STATE_FOR_REGISTRATION = [ACCEPTED, REGISTRATION_SUBMITTED, VALIDATED]
STATES_FOR_ARCHIVE = [
    ACCEPTED, REJECTED, REGISTRATION_STATE_CHOICES, WAITING, SUBMITTED, REGISTRATION_SUBMITTED, VALIDATED
]

ALL_CHOICE = ("", pgettext_lazy("plural", "All"))

BOOLEAN_CHOICES = (
    ALL_CHOICE,
    (True, _('Yes')),
    (False, _('No'))
)


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
            "{} - ".format(obj.partial_acronym) if obj.partial_acronym else "",
            obj.acronym,
            obj.academic_year,
        )


class AdmissionFilterForm(BootstrapForm):
    faculty = FacultyModelChoiceField(
        queryset=entity_version.find_latest_version(datetime.now())
                               .filter(entity_type=entity_type.FACULTY).order_by('acronym'),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Faculty')
    )

    formation = FormationModelChoiceField(
        queryset=None,
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Formation')
    )

    def __init__(self, *args, **kwargs):
        super(AdmissionFilterForm, self).__init__(*args, **kwargs)
        _build_formation_choices(self.fields['formation'], STATE_TO_DISPLAY)

    def get_admissions(self):
        return get_queryset_by_faculty_formation(self.cleaned_data['faculty'],
                                                 self.cleaned_data.get('formation'),
                                                 STATE_TO_DISPLAY,
                                                 False)


class RegistrationFilterForm(AdmissionFilterForm):

    ucl_registration_complete = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        required=False,
        label=_('Registered')
    )
    payment_complete = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        required=False,
        label=_('Paid')
    )
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(RegistrationFilterForm, self).__init__(*args, **kwargs)
        self.fields['state'].choices = _get_state_choices(REGISTRATION_STATE_CHOICES)
        _build_formation_choices(self.fields['formation'], STATE_FOR_REGISTRATION)

    def get_registrations(self):
        registered = self.cleaned_data.get('ucl_registration_complete')
        paid = self.cleaned_data.get('payment_complete')
        a_state = self.cleaned_data.get('state')

        qs = get_queryset_by_faculty_formation(self.cleaned_data['faculty'],
                                               self.cleaned_data.get('formation'),
                                               STATE_FOR_REGISTRATION, False)

        if registered:
            qs = qs.filter(ucl_registration_complete=registered)

        if paid:
            qs = qs.filter(payment_complete=paid)

        if a_state:
            qs = qs.filter(state=a_state)

        return qs


class ArchiveFilterForm(AdmissionFilterForm):
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(ArchiveFilterForm, self).__init__(*args, **kwargs)
        self.fields['state'].choices = _get_state_choices(ARCHIVE_STATE_CHOICES)
        _build_formation_choices(self.fields['formation'], STATES_FOR_ARCHIVE, True)

    def get_archives(self):
        a_state = self.cleaned_data.get('state')

        if a_state is None or a_state == '':
            a_state = STATES_FOR_ARCHIVE

        return get_queryset_by_faculty_formation(self.cleaned_data['faculty'],
                                                 self.cleaned_data.get('formation'),
                                                 a_state,
                                                 True)


def get_queryset_by_faculty_formation(faculty, formation, states, archived_status):

    if states:
        if isinstance(states, list):
            qs = Admission.objects.filter(
                state__in=states
            )
        else:
            qs = Admission.objects.filter(
                state=states
            )
    else:
        qs = Admission.objects.all()

    if faculty:
        qs = _get_filter_entity_management(
            qs,
            faculty.acronym,
            True
        )

    if formation:
        qs = qs.filter(formation=formation)

    qs = qs.filter(archived=archived_status)
    
    return qs.order_by('person_information')


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


def _build_formation_choices(field, states, archived_status=False):
    field.queryset = EducationGroupYear.objects \
        .filter(id__in=Admission.objects.filter(state__in=states, archived=archived_status)
                .values_list('formation', flat=False).distinct('formation')
                ).order_by('acronym')


def _get_state_choices(choices):
    return [ALL_CHOICE] + sorted(choices, key=itemgetter(1))


def _get_filter_entity_management(qs, requirement_entity_acronym, with_entity_subordinated):
    entity_ids = get_entities_ids(requirement_entity_acronym, with_entity_subordinated)
    return qs.filter(formation__management_entity__in=entity_ids)
