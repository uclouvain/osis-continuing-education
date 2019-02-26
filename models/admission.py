##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.db import models
from django.db.models import Manager
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from base.models.entity_version import EntityVersion
from base.models.enums.entity_type import FACULTY
from continuing_education.business.admission import send_state_changed_email, send_admission_submitted_email_to_admin, \
    send_admission_submitted_email_to_participant
from continuing_education.models.enums import admission_state_choices, enums
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin, SerializableModelManager

NEWLY_CREATED_STATE = "NEWLY_CREATED"


class RegistrationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED
        ])


class AdmissionManager(SerializableModelManager):
    def get_queryset(self):
        return super().get_queryset().exclude(state__in=[
            admission_state_choices.ACCEPTED,
            admission_state_choices.REGISTRATION_SUBMITTED,
            admission_state_choices.VALIDATED
        ])


class AdmissionAdmin(SerializableModelAdmin):
    list_display = ('person_information', 'formation', 'state')


class Admission(SerializableModel):

    CONTINUING_EDUCATION_TYPE = 8

    objects = Manager()
    admission_objects = AdmissionManager()
    registration_objects = RegistrationManager()

    person_information = models.ForeignKey(
        'continuing_education.ContinuingEducationPerson',
        blank=True,
        null=True,
        verbose_name=_("Person information")
    )

    formation = models.ForeignKey(
        'base.EducationGroupYear',
        on_delete=models.PROTECT,
        verbose_name=_("Formation")
    )

    # Contact
    citizenship = models.ForeignKey(
        'reference.Country',
        blank=True,
        null=True,
        related_name='citizenship',
        verbose_name=_("Citizenship")
    )
    address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        verbose_name=_("Address")
    )
    phone_mobile = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Mobile phone")
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
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
    professional_impact = models.TextField(
        blank=True,
        verbose_name=_("Professional impact")
    )

    # Awareness
    awareness_ucl_website = models.BooleanField(
        default=False,
        verbose_name=_("Awareness UCL website")
    )
    awareness_formation_website = models.BooleanField(
        default=False,
        verbose_name=_("Awareness formation website")
    )
    awareness_press = models.BooleanField(
        default=False,
        verbose_name=_("Awareness press")
    )
    awareness_facebook = models.BooleanField(
        default=False,
        verbose_name=_("Awareness Facebook")
    )
    awareness_linkedin = models.BooleanField(
        default=False,
        verbose_name=_("Awareness LinkedIn")
    )
    awareness_customized_mail = models.BooleanField(
        default=False,
        verbose_name=_("Awareness customized mail")
    )
    awareness_emailing = models.BooleanField(
        default=False,
        verbose_name=_("Awareness emailing")
    )
    awareness_other = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Awareness other")
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
        verbose_name=_("Billing address")
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
        verbose_name=_("Previous ucl registration")
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
        verbose_name=_("Residence address")
    )

    residence_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Residence phone")
    )

    # Student Sheet
    ucl_registration_complete = models.BooleanField(
        default=False,
        verbose_name=_("UCL registration complete")
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

    # TODO:: Add dates of followed courses
    sessions = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Sessions")
    )

    archived = models.BooleanField(
        default=False,
        verbose_name=_("Archived")
    )

    @property
    def formation_display(self):
        return "{}{} - {}".format(
            "{} - ".format(self.formation.partial_acronym) if self.formation.partial_acronym else "",
            self.formation.acronym,
            self.formation.academic_year,
        )

    def is_draft(self):
        return self.state == admission_state_choices.DRAFT

    def is_submitted(self):
        return self.state == admission_state_choices.SUBMITTED

    def is_accepted(self):
        return self.state == admission_state_choices.ACCEPTED

    def is_rejected(self):
        return self.state == admission_state_choices.REJECTED

    def is_waiting(self):
        return self.state == admission_state_choices.WAITING

    def is_registration_submitted(self):
        return self.state == admission_state_choices.REGISTRATION_SUBMITTED

    def is_validated(self):
        return self.state == admission_state_choices.VALIDATED

    def get_faculty(self):
        education_group_year = self.formation
        if education_group_year:
            management_entity = education_group_year.management_entity
            entity = EntityVersion.objects.filter(entity=management_entity).first()
            if entity and entity.entity_type == FACULTY:
                return management_entity
            else:
                return _get_faculty_parent(management_entity)
        else:
            return None

    class Meta:
        permissions = (
            ("can_access_admission", "Can consult IUFC admission information"),
            ("can_validate_registration", "Can validate IUFC registration file"),
        )


def search(**kwargs):
    qs = Admission.objects

    if "person" in kwargs:
        # TODO :: Update this condition when link to student is done
        qs = qs.filter(person_information=kwargs['person'])

    if "state" in kwargs:
        qs = qs.filter(state=kwargs['state'])

    return qs


def _get_faculty_parent(management_entity):
    faculty = EntityVersion.objects.filter(entity=management_entity).first()
    if faculty:
        return faculty.parent


# TODO :: dismiss use of signal when API is used
@receiver(pre_save, sender=Admission)
def admission_pre_save_callback(sender, instance, **kwargs):
    try:
        instance._original_state = Admission.objects.get(pk=instance.pk).state
    except Admission.DoesNotExist:
        instance._original_state = NEWLY_CREATED_STATE


# TODO :: dismiss use of signal when API is used
@receiver(post_save, sender=Admission)
def admission_post_save_callback(sender, instance, created, **kwargs):
    try:
        if instance.state != instance._original_state and instance._original_state != NEWLY_CREATED_STATE:
            if instance.state == admission_state_choices.SUBMITTED:
                send_admission_submitted_email_to_admin(instance)
                send_admission_submitted_email_to_participant(instance)
            elif instance.state != admission_state_choices.DRAFT:
                send_state_changed_email(instance)
    except AttributeError:
        pass
