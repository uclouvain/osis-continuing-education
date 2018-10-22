from django.db import models
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.enums import admission_state_choices, enums
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AdmissionAdmin(SerializableModelAdmin):
    list_display = ('person_information', 'formation', 'state')


class Admission(SerializableModel):

    CONTINUING_EDUCATION_TYPE = 8

    person_information = models.ForeignKey(
        'continuing_education.ContinuingEducationPerson',
        blank=True,
        null=True,
        verbose_name=_("person_information")
    )

    # Contact
    citizenship = models.ForeignKey(
        'reference.Country',
        blank=True,
        null=True,
        related_name='citizenship',
        verbose_name=_("citizenship")
    )
    address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        verbose_name=_("address")
    )
    phone_mobile = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("phone_mobile")
    )
    email = models.EmailField(
        max_length=255,
        blank=True,
        verbose_name=_("email")
    )

    # Education
    high_school_diploma = models.BooleanField(
        default=False,
        verbose_name=_("high_school_diploma")
    )
    high_school_graduation_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("high_school_graduation_year")
    )
    last_degree_level = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("last_degree_level")
    )
    last_degree_field = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("last_degree_field")
    )
    last_degree_institution = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("last_degree_institution")
    )
    last_degree_graduation_year = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_("last_degree_graduation_year")
    )
    other_educational_background = models.TextField(
        blank=True,
        verbose_name=_("other_educational_background")
    )

    # Professional Background
    professional_status = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.STATUS_CHOICES,
        verbose_name=_("professional_status")
    )
    current_occupation = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("current_occupation")
    )
    current_employer = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("current_employer")
    )
    activity_sector = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.SECTOR_CHOICES,
        verbose_name=_("activity_sector")
    )
    past_professional_activities = models.TextField(
        blank=True,
        verbose_name=_("past_professional_activities")
    )

    # Motivation
    motivation = models.TextField(
        blank=True,
        verbose_name=_("motivation")
    )
    professional_impact = models.TextField(
        blank=True,
        verbose_name=_("professional_impact")
    )

    # Temporarily simplifying getting formation
    formation = models.CharField(
        max_length=50,
        verbose_name=_("formation")
    )

    # Awareness
    awareness_ucl_website = models.BooleanField(
        default=False,
        verbose_name=_("awareness_ucl_website")
    )
    awareness_formation_website = models.BooleanField(
        default=False,
        verbose_name=_("awareness_formation_website")
    )
    awareness_press = models.BooleanField(
        default=False,
        verbose_name=_("awareness_press")
    )
    awareness_facebook = models.BooleanField(
        default=False,
        verbose_name=_("awareness_facebook")
    )
    awareness_linkedin = models.BooleanField(
        default=False,
        verbose_name=_("awareness_linkedin")
    )
    awareness_customized_mail = models.BooleanField(
        default=False,
        verbose_name=_("awareness_customized_mail")
    )
    awareness_emailing = models.BooleanField(
        default=False,
        verbose_name=_("awareness_emailing")
    )

    # State
    state = models.CharField(
        max_length=50,
        blank=True,
        choices=admission_state_choices.STATE_CHOICES,
        default=admission_state_choices.DRAFT,
        verbose_name=_("state")
    )

    # Billing
    registration_type = models.CharField(
        max_length=50,
        blank=True,
        choices=enums.REGISTRATION_TITLE_CHOICES,
        verbose_name=_("registration_type")
    )
    use_address_for_billing = models.BooleanField(
        default=False,
        verbose_name=_("use_address_for_billing")
    )
    billing_address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        related_name="billing_address",
        verbose_name=_("billing_address")
    )

    head_office_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("head_office_name")
    )
    company_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("company_number")
    )
    vat_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("vat_number")
    )

    # Registration
    national_registry_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("national_registry_number")
    )
    id_card_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("id_card_number")
    )
    passport_number = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("passport_number")
    )
    marital_status = models.CharField(
        max_length=255,
        blank=True,
        choices=enums.MARITAL_STATUS_CHOICES,
        verbose_name=_("marital_status")
    )
    spouse_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("spouse_name")
    )
    children_number = models.SmallIntegerField(
        blank=True,
        default=0,
        verbose_name=_("children_number")
    )
    previous_ucl_registration = models.BooleanField(
        default=False,
        verbose_name=_("previous_ucl_registration")
    )
    previous_noma = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("previous_noma")
    )

    # Post
    use_address_for_post = models.BooleanField(
        default=False,
        verbose_name=_("use_address_for_post")
    )
    residence_address = models.ForeignKey(
        'continuing_education.Address',
        blank=True,
        null=True,
        related_name="residence_address",
        verbose_name=_("residence_address")
    )

    residence_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("residence_phone")
    )

    # Student Sheet
    registration_complete = models.BooleanField(
        default=False,
        verbose_name=_("registration_complete")
    )
    noma = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("noma")
    )
    payment_complete = models.BooleanField(
        default=False,
        verbose_name=_("payment_complete")
    )
    formation_spreading = models.BooleanField(
        default=False,
        verbose_name=_("formation_spreading")
    )
    prior_experience_validation = models.BooleanField(
        default=False,
        verbose_name=_("prior_experience_validation")
    )
    assessment_presented = models.BooleanField(
        default=False,
        verbose_name=_("assessment_presented")
    )
    assessment_succeeded = models.BooleanField(
        default=False,
        verbose_name=_("assessment_succeeded")
    )

    # TODO:: Add dates of followed courses
    sessions = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("sessions")
    )


def search(**kwargs):
    qs = Admission.objects

    if "person" in kwargs:
        # TODO :: Update this condition when link to student is done
        qs = qs.filter(person_information=kwargs['person'])

    if "state" in kwargs:
        qs = qs.filter(state=kwargs['state'])

    return qs
