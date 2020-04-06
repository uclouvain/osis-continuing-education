##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import uuid as uuid

from django.contrib.admin import ModelAdmin
from django.core.exceptions import PermissionDenied
from django.db import models
from django.db.models import Manager, Model
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin

from continuing_education.auth.roles.continuing_education_training_manager import ContinuingEducationTrainingManager
from continuing_education.models.enums import admission_state_choices, enums, ucl_registration_state_choices
from osis_common.utils.models import get_object_or_none

NEWLY_CREATED_STATE = "NEWLY_CREATED"


class RegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED

        ])


class AdmissionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED
        ])


class AdmissionAdmin(VersionAdmin, ModelAdmin):
    list_display = ('person_information', 'formation', 'state')


class Admission(Model):
    CONTINUING_EDUCATION_TYPE = 8

    objects = Manager()
    admission_objects = AdmissionManager()
    registration_objects = RegistrationManager()

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    person_information = models.ForeignKey(
        'continuing_education.ContinuingEducationPerson',
        blank=True,
        null=True,
        verbose_name=_("Person information"),
        on_delete=models.CASCADE
    )

    formation = models.ForeignKey(
        'continuing_education.ContinuingEducationTraining',
        on_delete=models.PROTECT,
        verbose_name=_("Formation")
    )

    academic_year = models.ForeignKey(
        'base.AcademicYear',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name=_("Academic year")
    )

    # Contact
    citizenship = models.ForeignKey(
        'reference.Country',
        blank=True,
        null=True,
        related_name='citizenship',
        verbose_name=_("Citizenship"),
        on_delete=models.CASCADE
    )
    address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        verbose_name=_("Address"),
        on_delete=models.CASCADE
    )
    phone_mobile = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Mobile phone")
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Email")
    )

    # Education
    high_school_diploma = models.BooleanField(
        default=False,
        verbose_name=_("High school diploma")
    )
    high_school_graduation_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("High school graduation year")
    )
    last_degree_level = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Last degree level")
    )
    last_degree_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Last degree field")
    )
    last_degree_institution = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Last degree institution")
    )
    last_degree_graduation_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Last degree graduation year")
    )
    other_educational_background = models.TextField(
        blank=True,
        verbose_name=_("Other educational background")
    )

    # Professional Background
    professional_status = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.STATUS_CHOICES,
        verbose_name=_("Professional status")
    )
    current_occupation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Current occupation")
    )
    current_employer = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Current employer")
    )
    activity_sector = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.SECTOR_CHOICES,
        verbose_name=_("Activity sector")
    )
    past_professional_activities = models.TextField(
        blank=True,
        verbose_name=_("Past professional activities")
    )

    # Motivation
    motivation = models.TextField(
        blank=True,
        verbose_name=_("Motivation")
    )
    professional_personal_interests = models.TextField(
        blank=True,
        verbose_name=_("Professional and personal interests")
    )

    # Awareness
    awareness_ucl_website = models.BooleanField(
        default=False,
        verbose_name=_("By UCLouvain website")
    )
    awareness_formation_website = models.BooleanField(
        default=False,
        verbose_name=_("By formation website")
    )
    awareness_press = models.BooleanField(
        default=False,
        verbose_name=_("By press")
    )
    awareness_facebook = models.BooleanField(
        default=False,
        verbose_name=_("By Facebook")
    )
    awareness_linkedin = models.BooleanField(
        default=False,
        verbose_name=_("By LinkedIn")
    )
    awareness_customized_mail = models.BooleanField(
        default=False,
        verbose_name=_("By customized mail")
    )
    awareness_emailing = models.BooleanField(
        default=False,
        verbose_name=_("By emailing")
    )
    awareness_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Other")
    )
    awareness_word_of_mouth = models.BooleanField(
        default=False,
        verbose_name=_("By word of mouth")
    )
    awareness_friends = models.BooleanField(
        default=False,
        verbose_name=_("By friends")
    )
    awareness_former_students = models.BooleanField(
        default=False,
        verbose_name=_("By former students")
    )
    awareness_moocs = models.BooleanField(
        default=False,
        verbose_name=_("By Moocs")
    )
    # State
    state = models.CharField(
        max_length=50,
        blank=True,
        choices=admission_state_choices.STATE_CHOICES,
        default=admission_state_choices.DRAFT,
        verbose_name=_("State")
    )

    state_reason = models.TextField(
        blank=True,
        verbose_name=_("State reason")
    )

    # Billing
    registration_type = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.REGISTRATION_TITLE_CHOICES,
        verbose_name=_("Registration type")
    )
    use_address_for_billing = models.BooleanField(
        default=False,
        verbose_name=_("Use address for billing")
    )
    billing_address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        related_name="billing_address",
        verbose_name=_("Billing address"),
        on_delete=models.CASCADE
    )

    head_office_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Head office name")
    )
    company_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Company number")
    )
    vat_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("VAT number")
    )

    # Registration
    national_registry_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("National registry number")
    )
    id_card_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("ID card number")
    )
    passport_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Passport number")
    )
    marital_status = models.CharField(
        max_length=255,
        blank=True,
        choices=enums.MARITAL_STATUS_CHOICES,
        verbose_name=_("Marital status")
    )
    spouse_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Spouse name")
    )
    children_number = models.SmallIntegerField(
        blank=True,
        default=0,
        verbose_name=_("Children number")
    )
    previous_ucl_registration = models.BooleanField(
        default=False,
        verbose_name=_("Previous uclouvain registration")
    )
    previous_noma = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Previous NOMA")
    )

    # Post
    use_address_for_post = models.BooleanField(
        default=False,
        verbose_name=_("Use address for post")
    )
    residence_address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        related_name="residence_address",
        verbose_name=_("Residence address"),
        on_delete=models.CASCADE
    )

    residence_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Residence phone")
    )

    # Student Sheet
    ucl_registration_complete = models.CharField(
        max_length=50,
        blank=True,
        choices=ucl_registration_state_choices.STATE_CHOICES,
        default=ucl_registration_state_choices.INIT_STATE,
        verbose_name=_("UCLouvain registration complete")
    )

    noma = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("NOMA")
    )
    payment_complete = models.BooleanField(
        default=False,
        verbose_name=_("Payment complete")
    )
    formation_spreading = models.BooleanField(
        default=False,
        verbose_name=_("Formation spreading")
    )
    prior_experience_validation = models.BooleanField(
        default=False,
        verbose_name=_("Prior experience validation")
    )
    assessment_presented = models.BooleanField(
        default=False,
        verbose_name=_("Assessment presented")
    )
    assessment_succeeded = models.BooleanField(
        default=False,
        verbose_name=_("Assessment succeeded")
    )
    registration_file_received = models.BooleanField(
        default=False,
        verbose_name=_("Registration file received")
    )
    archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived")
    )
    diploma_produced = models.BooleanField(
        default=False,
        verbose_name=_("Diploma produced")
    )

    # TODO:: Add dates of followed courses
    sessions = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Sessions")
    )

    reduced_rates = models.BooleanField(
        default=False,
        verbose_name=_("Reduced rates")
    )

    spreading_payments = models.BooleanField(
        default=False,
        verbose_name=_("Spreading payments")
    )

    condition_of_acceptance = models.TextField(
        blank=True,
        verbose_name=_("Condition of acceptance")
    )

    additional_information = models.TextField(
        blank=True,
        verbose_name=_("Additional information")
    )

    comment = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_("Comment"),
    )

    @property
    def formation_display(self):
        education_group_year = self.formation.get_most_recent_education_group_year()
        return get_formation_display(
            education_group_year.partial_acronym,
            education_group_year.acronym,
            education_group_year.title,
            education_group_year.academic_year
        )

    @property
    def complete_contact_address(self):
        return _build_address(self.address)

    @property
    def complete_residence_address(self):
        return _build_address(self.residence_address)

    @property
    def complete_billing_address(self):
        return _build_address(self.billing_address)

    @property
    def awareness_list(self):
        list_awareness = [
            self._get_awareness_values(field)
            for field in Admission._meta.get_fields()
            if 'awareness_' in field.name and self._get_awareness_values(field)
            ]
        return ", ".join(list_awareness)

    def _get_awareness_values(self, field):
        if getattr(self, field.name) is True:
            return str(_(field.verbose_name))
        elif self._has_awareness_other(field):
            return "{} : {}".format(_('Other'), getattr(self, field.name))

    def _has_awareness_other(self, field):
        return isinstance(getattr(self, field.name), str) and field.name == "awareness_other" and len(
            getattr(self, field.name)) > 0

    def is_draft(self):
        return self.state == admission_state_choices.DRAFT

    def is_submitted(self):
        return self.state == admission_state_choices.SUBMITTED

    def is_accepted(self):
        return self.state == admission_state_choices.ACCEPTED

    def is_accepted_no_registration_required(self):
        return self.state == admission_state_choices.ACCEPTED_NO_REGISTRATION_REQUIRED

    def is_rejected(self):
        return self.state == admission_state_choices.REJECTED

    def is_waiting(self):
        return self.state == admission_state_choices.WAITING

    def is_registration_submitted(self):
        return self.state == admission_state_choices.REGISTRATION_SUBMITTED or \
               hasattr(self, '_original_state') and \
               getattr(self, '_original_state') == admission_state_choices.REGISTRATION_SUBMITTED

    def is_validated(self):
        return self.state == admission_state_choices.VALIDATED

    def is_cancelled(self):
        return self.state == admission_state_choices.CANCELLED

    def is_cancelled_no_registration_required(self):
        return self.state == admission_state_choices.CANCELLED_NO_REGISTRATION_REQUIRED

    def is_registration(self):
        return self.is_accepted() or self.is_validated() or self.is_registration_submitted()

    def is_admission(self):
        return self.is_waiting() or self.is_rejected() or self.is_submitted()

    def get_faculty(self):
        education_group_year = self.formation.get_most_recent_education_group_year()
        return education_group_year.management_entity

    class Meta:
        default_permissions = ['view', 'change']
        ordering = ('formation', 'person_information',)
        permissions = (
            ("validate_registration", "Validate IUFC registration file"),
            ("change_received_file_state", "Change received file state"),
            ("link_admission_to_academic_year", "Link an admission to an academic year"),
            ("inject_admission_to_epc", "Inject an admission to EPC"),
            ("mark_diploma_produced", "Mark an admission diploma has been produced"),
            ("send_notification", "Send a notification related to an admission"),
            ("archive_admission", "Archive an admission"),
            ("export_admission", "Export an admission into XLSX file"),
            ("cancel_admission", "Cancel an admission"),
        )


def search(**kwargs):
    qs = Admission.objects

    if "person" in kwargs:
        # TODO :: Update this condition when link to student is done
        qs = qs.filter(person_information=kwargs['person'])

    if "state" in kwargs:
        qs = qs.filter(state=kwargs['state'])

    return qs


def get_formation_display(partial_acronym, acronym, title, academic_year):
    return "{}{} - {} - {}".format(
        "{} - ".format(partial_acronym) if partial_acronym else "",
        acronym,
        title,
        academic_year,
    )


def filter_authorized_admissions(user, admission_list):
    if not user.has_perm('continuing_education.manage_all_trainings'):
        person_trainings = ContinuingEducationTrainingManager.objects.filter(
            person=user.person
        ).values_list('training', flat=True)
        admission_list = admission_list.filter(formation_id__in=person_trainings)
    return admission_list


def can_access_admission(user, admission):
    if admission not in filter_authorized_admissions(user, Admission.objects.all()):
        raise PermissionDenied


def _build_address(address):
    if address:
        return "{} - {} {} {}".format(address.location if address.location else '',
                                      address.postal_code if address.postal_code else '',
                                      address.city.upper() if address.city else '',
                                      "- {}".format(address.country.name.upper()) if address.country else '')
    return ''


def admission_getter(request, *view_args, **view_kwargs):
    return get_object_or_none(Admission, id=view_kwargs.get('admission_id'))
