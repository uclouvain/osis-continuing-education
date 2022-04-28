
from datetime import datetime
from operator import itemgetter

from django import forms
from django.db.models import Q
from django.forms import ModelChoiceField
from django.utils.translation import gettext_lazy as _, pgettext
from django.utils.translation import pgettext_lazy

from base.business.entity import get_entities_ids
from base.models import entity_version
from base.models.academic_year import AcademicYear
from base.models.education_group import EducationGroup
from base.models.entity_version import EntityVersion
from base.models.enums import entity_type
from base.models.person import Person
from continuing_education.auth.roles.continuing_education_training_manager import ContinuingEducationTrainingManager
from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_training import CONTINUING_EDUCATION_TRAINING_TYPES, \
    ContinuingEducationTraining
from continuing_education.models.enums.admission_state_choices import REGISTRATION_STATE_CHOICES, \
    ADMISSION_STATE_CHOICES
from continuing_education.models.enums.admission_state_choices import REJECTED, SUBMITTED, WAITING, ACCEPTED, \
    REGISTRATION_SUBMITTED, VALIDATED, STATE_CHOICES, ARCHIVE_STATE_CHOICES, DRAFT, ACCEPTED_NO_REGISTRATION_REQUIRED
from continuing_education.models.prospect import Prospect

STATE_TO_DISPLAY = [SUBMITTED, REJECTED, WAITING, DRAFT, ACCEPTED_NO_REGISTRATION_REQUIRED]
STATE_FOR_REGISTRATION = [ACCEPTED, REGISTRATION_SUBMITTED, VALIDATED]
STATE_FOR_REGISTRATION_CONTINUING_MANAGER = [ACCEPTED, REGISTRATION_SUBMITTED]
STATES_FOR_ARCHIVE = [
    ACCEPTED, REJECTED, REGISTRATION_STATE_CHOICES, WAITING, SUBMITTED, REGISTRATION_SUBMITTED, VALIDATED,
    ACCEPTED_NO_REGISTRATION_REQUIRED
]

ALL_CHOICE = ("", pgettext_lazy("plural", "All"))

BOOLEAN_CHOICES = (
    ALL_CHOICE,
    (True, _('Yes')),
    (False, _('No'))
)

ACTIVE = _("Active")
INACTIVE = _("Inactive")
NOT_ORGANIZED = _("Not organized")
FORMATION_STATE_CHOICES = [
    ALL_CHOICE,
    (ACTIVE, _('Active')),
    (INACTIVE, _('Inactive')),
    (NOT_ORGANIZED, _('Not organized')),
]


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
        return obj.acronym_and_title


class CommonFilterForm(BootstrapForm):
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

    free_text = forms.CharField(max_length=100, required=False, label=_('In all fields'))

    registration_required = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        required=False,
        label=_('Registration required')
    )

    def __init__(self, data=None, *args, **kwargs):
        super(CommonFilterForm, self).__init__(data, *args, **kwargs)
        _build_formation_choices(self.fields['formation'], STATE_TO_DISPLAY)

    def get_admissions(self):
        state_filter = self.cleaned_data.get('state')
        free_text = self.cleaned_data.get('free_text')
        registration_required = self.cleaned_data.get('registration_required')

        qs = get_queryset_by_faculty_formation(
            self.cleaned_data['faculty'],
            self.cleaned_data.get('formation'),
            STATE_TO_DISPLAY,
            False
        )

        if state_filter:
            if isinstance(state_filter, str):
                qs = qs.filter(state=state_filter)
            if isinstance(state_filter, list):
                qs = qs.filter(state__in=state_filter)

        if free_text:
            qs = search_admissions_with_free_text(free_text, qs)

        if registration_required:
            qs = qs.filter(formation__registration_required=registration_required)

        return qs.select_related(
            'person_information__person',
            'formation__education_group'
        )


def search_admissions_with_free_text(free_text, qs):
    qs = qs.filter(
        Q(person_information__person__first_name__unaccent__icontains=free_text) |
        Q(person_information__person__last_name__unaccent__icontains=free_text) |
        Q(person_information__person__email__icontains=free_text) |
        Q(email__icontains=free_text) |
        Q(formation__education_group__educationgroupyear__acronym__icontains=free_text) |
        Q(formation__education_group__educationgroupyear__title__unaccent__icontains=free_text) |
        Q(address__country__name__unaccent__icontains=free_text) |
        Q(address__city__unaccent__icontains=free_text)
    ).distinct()
    return qs


class AdmissionFilterForm(CommonFilterForm):

    def __init__(self, data=None, *args, **kwargs):
        state_default_attrs = {}
        if data is None or data.get('state') is None:
            #  If no state pre-selected, all states are selected by default
            state_default_attrs = {'checked': True}
        super(AdmissionFilterForm, self).__init__(data, *args, **kwargs)
        choices = sorted(ADMISSION_STATE_CHOICES, key=itemgetter(1))

        self.fields['state'] = forms.MultipleChoiceField(
            widget=forms.CheckboxSelectMultiple(attrs=state_default_attrs),
            choices=choices,
            required=False
        )


class RegistrationFilterForm(CommonFilterForm):

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

    registration_file_received = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=False)
    academic_year = forms.ModelChoiceField(
        queryset=AcademicYear.objects.filter(year__gte=2018),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Academic year')
    )

    def __init__(self, *args, user=None, **kwargs):
        super(RegistrationFilterForm, self).__init__(*args, **kwargs)
        self.fields['state'].choices = _get_state_choices(REGISTRATION_STATE_CHOICES)
        self.states_filter = STATE_FOR_REGISTRATION
        _build_formation_choices(self.fields['formation'], self.states_filter)

    def get_registrations(self):
        registered = self.cleaned_data.get('ucl_registration_complete')
        paid = self.cleaned_data.get('payment_complete')
        a_state = self.cleaned_data.get('state')
        free_text = self.cleaned_data.get('free_text')
        academic_year = self.cleaned_data.get('academic_year')

        qs = get_queryset_by_faculty_formation(self.cleaned_data['faculty'],
                                               self.cleaned_data.get('formation'),
                                               self.states_filter,
                                               False,
                                               self.cleaned_data.get('registration_file_received'))

        if registered:
            qs = qs.filter(ucl_registration_complete=registered)

        if paid:
            qs = qs.filter(payment_complete=paid)

        if a_state:
            qs = qs.filter(state=a_state)

        if free_text:
            qs = search_admissions_with_free_text(free_text, qs)

        if academic_year:
            qs = qs.filter(academic_year=academic_year)

        return qs.select_related(
            'person_information__person',
            'formation__education_group',
            'academic_year',
        )


class ArchiveFilterForm(CommonFilterForm):
    state = forms.ChoiceField(
        choices=STATE_CHOICES,
        required=False
    )

    def __init__(self, data, user=None, *args, **kwargs):
        super(ArchiveFilterForm, self).__init__(data, *args, **kwargs)
        self.fields['state'].choices = _get_state_choices(ARCHIVE_STATE_CHOICES)
        _build_formation_choices(self.fields['formation'], STATES_FOR_ARCHIVE, True)
        if user and not user.groups.filter(name='continuing_education_managers').exists():
            self.fields['formation'].queryset = self.fields['formation'].queryset.filter(
                managers=user.person
            )

    def get_archives(self):
        a_state = self.cleaned_data.get('state')
        free_text = self.cleaned_data.get('free_text')

        if a_state is None or a_state == '':
            a_state = STATES_FOR_ARCHIVE
        else:
            if a_state == ACCEPTED:
                a_state = [ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED]

        qs = get_queryset_by_faculty_formation(
            self.cleaned_data['faculty'],
            self.cleaned_data.get('formation'),
            a_state,
            True
        )
        if free_text:
            qs = search_admissions_with_free_text(free_text, qs)

        return qs.select_related(
            'person_information__person',
            'formation'
        )


def get_queryset_by_faculty_formation(faculty, formation, states, archived_status, received_file=None):
    qs = Admission.objects.all()

    if states:
        if isinstance(states, list):
            qs = Admission.objects.filter(
                state__in=states
            )
        else:
            qs = Admission.objects.filter(
                state=states
            )

    if faculty:
        qs = _get_filter_entity_management(
            qs,
            faculty.acronym,
            True
        )

    if formation:
        qs = qs.filter(formation=formation)

    qs = qs.filter(archived=archived_status)

    if received_file:
        qs = qs.filter(registration_file_received=received_file)

    return qs.formations()


def _build_formation_choices(field, states, archived_status=False):
    field.queryset = ContinuingEducationTraining.objects.formations().filter(
        id__in=Admission.objects.filter(
            state__in=states,
            archived=archived_status
        ).values_list('formation', flat=False)
    )


def _get_state_choices(choices):
    return [ALL_CHOICE] + sorted(choices, key=itemgetter(1))


def _get_filter_entity_management(qs, requirement_entity_acronym, with_entity_subordinated):
    entity_ids = get_entities_ids(requirement_entity_acronym, with_entity_subordinated)
    return qs.filter(formation__education_group__educationgroupyear__management_entity__in=entity_ids).distinct()


class FormationFilterForm(CommonFilterForm):
    acronym = forms.CharField(max_length=40, required=False, label=_('Acronym'))
    title = forms.CharField(max_length=50, required=False, label=_('Title'))
    state = forms.ChoiceField(choices=FORMATION_STATE_CHOICES, required=False, label=_('State'))
    training_aid = forms.ChoiceField(choices=BOOLEAN_CHOICES, required=False, label=_('Training aid'))
    free_text = forms.CharField(max_length=100, required=False, label=_('In all fields'))

    def __init__(self, *args, **kwargs):
        super(FormationFilterForm, self).__init__(*args, **kwargs)
        self.fields['state'].choices = FORMATION_STATE_CHOICES

    def get_formations(self):
        faculty = self.cleaned_data.get('faculty')
        acronym = self.cleaned_data.get('acronym')
        title = self.cleaned_data.get('title')
        training_aid = self.cleaned_data.get('training_aid')
        free_text = self.cleaned_data.get('free_text')

        qs = EducationGroup.objects.filter(
            educationgroupyear__education_group_type__name__in=CONTINUING_EDUCATION_TRAINING_TYPES,
        )

        qs = _build_active_parameter(qs, self.cleaned_data.get('state'))
        if faculty:
            qs = _get_formation_filter_entity_management(
                qs,
                faculty.acronym,
                True
            )

        if acronym:
            qs = qs.filter(
                Q(educationgroupyear__acronym__icontains=acronym) |
                Q(educationgroupyear__partial_acronym__icontains=acronym))

        if title:
            qs = qs.filter(educationgroupyear__title__icontains=title)

        if training_aid:
            qs = qs.filter(continuingeducationtraining__training_aid=training_aid)

        if free_text:
            qs = qs.filter(
                Q(educationgroupyear__acronym__icontains=free_text) |
                Q(educationgroupyear__title__icontains=free_text)
            )

        return qs.select_related('continuingeducationtraining').order_by('educationgroupyear__acronym').distinct()


def _build_active_parameter(qs, state):
    if state in (ACTIVE, INACTIVE):
        active_state = state == ACTIVE
        return qs.filter(continuingeducationtraining__active=active_state)
    elif state == NOT_ORGANIZED:
        return qs.filter(continuingeducationtraining__isnull=True)
    return qs


def _get_formation_filter_entity_management(qs, requirement_entity_acronym, with_entity_subordinated):
    exact_requirement_entity_acronym = "^{}$".format(requirement_entity_acronym)
    entity_ids = get_entities_ids(exact_requirement_entity_acronym, with_entity_subordinated)
    return qs.filter(educationgroupyear__management_entity__in=entity_ids)


class ManagerFilterForm(BootstrapForm):
    person = ModelChoiceField(
        queryset=Person.objects.filter(
            user__groups__name='continuing_education_training_managers'
        ).order_by('last_name'),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Manager')
    )

    faculty = FacultyModelChoiceField(
        queryset=entity_version.find_latest_version(datetime.now())
                               .filter(entity_type=entity_type.FACULTY).order_by('acronym'),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Faculty')
    )

    training = FormationModelChoiceField(
        queryset=ContinuingEducationTraining.objects.filter(
            id__in=ContinuingEducationTrainingManager.objects.values_list('training', flat=True)
        ),
        widget=forms.Select(),
        empty_label=pgettext("plural", "All"),
        required=False,
        label=_('Formation')
    )

    def __init__(self, *args, **kwargs):
        super(ManagerFilterForm, self).__init__(*args, **kwargs)

    def get_managers(self):
        training = self.cleaned_data.get('training')
        person = self.cleaned_data.get('person')
        faculty = self.cleaned_data.get('faculty')
        qs = Person.objects.filter(user__groups__name='continuing_education_training_managers').order_by('last_name')
        if training:
            qs = qs.filter(
                id__in=ContinuingEducationTrainingManager.objects.filter(
                    training=training
                ).values_list('person__id')
            )
        if person:
            qs = qs.filter(
                id__in=ContinuingEducationTrainingManager.objects.filter(
                    person=person
                ).values_list('person__id')
            )
        if faculty:
            entity = EntityVersion.objects.filter(id=faculty.id).first().entity
            trainings_by_faculty = ContinuingEducationTraining.objects.filter(
                education_group__educationgroupyear__management_entity=entity
            )
            qs = qs.filter(
                id__in=ContinuingEducationTrainingManager.objects.filter(
                    training__in=trainings_by_faculty
                ).values_list('person__id')
            )
        return qs


class ProspectFilterForm(CommonFilterForm):

    def __init__(self, data, user=None, *args, **kwargs):
        super(ProspectFilterForm, self).__init__(data, *args, **kwargs)
        self.prospects_queryset = self.get_prospects_by_user(user)
        _build_prospects_formation_choices(self.fields['formation'], self.prospects_queryset)

    def get_prospects_by_user(self, user):
        person_trainings = ContinuingEducationTrainingManager.objects.filter(
            person=user.person
        ).values_list('training', flat=True)
        return Prospect.objects.filter(formation_id__in=person_trainings)

    def get_propects_with_filter(self):
        qs = self.prospects_queryset
        formation = self.cleaned_data.get('formation')
        free_text = self.cleaned_data.get('free_text')
        if formation:
            qs = qs.filter(
                id__in=Prospect.objects.filter(
                    formation=formation
                ).values_list('id')
            )

        if free_text:
            qs = qs.filter(
                Q(first_name__unaccent__icontains=free_text) |
                Q(name__unaccent__icontains=free_text) |
                Q(email__icontains=free_text) |
                Q(phone_number__icontains=free_text) |
                Q(formation__education_group__educationgroupyear__acronym__icontains=free_text) |
                Q(formation__education_group__educationgroupyear__title__unaccent__icontains=free_text) |
                Q(postal_code__icontains=free_text) |
                Q(city__unaccent__icontains=free_text)
            ).distinct()
        return qs


def _build_prospects_formation_choices(field, prospects_queryset):
    prospect_ids = [prospect.id for prospect in list(prospects_queryset)]

    field.queryset = ContinuingEducationTraining.objects.formations().filter(
        id__in=Prospect.objects.filter(id__in=prospect_ids).values_list('formation', flat=False)
    ).distinct().order_by('education_group__educationgroupyear__acronym')
