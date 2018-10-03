from django.contrib.admin import ModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.enums.enums import STATE_CHOICES, REGISTRATION_TITLE_CHOICES, MARITAL_STATUS_CHOICES
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class AdmissionAdmin(SerializableModelAdmin):
    list_display = ('person_information', 'formation', 'state')


class Admission(SerializableModel):

    CONTINUING_EDUCATION_TYPE = 8

    person_information = models.ForeignKey('continuing_education.ContinuingEducationPerson', blank=True, null=True,
                                           verbose_name=_("person_information"))

    #Motivation
    motivation = models.TextField(blank=True, verbose_name=_("motivation"))
    professional_impact = models.TextField(blank=True, verbose_name=_("professional_impact"))

    # temporarily simplifying getting formation
    formation = models.CharField(max_length=50, verbose_name=_("formation"))

    #Awareness
    awareness_ucl_website = models.BooleanField(default=False, verbose_name=_("awareness_ucl_website"))
    awareness_formation_website = models.BooleanField(default=False, verbose_name=_("awareness_formation_website"))
    awareness_press = models.BooleanField(default=False, verbose_name=_("awareness_press"))
    awareness_facebook = models.BooleanField(default=False, verbose_name=_("awareness_facebook"))
    awareness_linkedin = models.BooleanField(default=False, verbose_name=_("awareness_linkedin"))
    awareness_customized_mail = models.BooleanField(default=False, verbose_name=_("awareness_customized_mail"))
    awareness_emailing = models.BooleanField(default=False, verbose_name=_("awareness_emailing"))

    #State
    state = models.CharField(max_length=50, blank=True,  choices=STATE_CHOICES, verbose_name=_("state"))

    #Billing
    registration_type = models.CharField(max_length=50, blank=True, choices=REGISTRATION_TITLE_CHOICES,
                                         verbose_name=_("registration_type"))
    use_address_for_billing = models.BooleanField(default=False, verbose_name=_("use_address_for_billing"))
    billing_address = models.ForeignKey('continuing_education.Address', blank=True, null=True,
                                        related_name="billing_address", verbose_name=_("billing_address"))

    head_office_name = models.CharField(max_length=255, blank=True, verbose_name=_("head_office_name"))
    company_number = models.CharField(max_length=255, blank=True, verbose_name=_("company_number"))
    vat_number = models.CharField(max_length=255, blank=True, verbose_name=_("vat_number"))

    #Registration
    national_registry_number = models.CharField(max_length=255, blank=True, verbose_name=_("national_registry_number"))
    id_card_number = models.CharField(max_length=255, blank=True, verbose_name=_("id_card_number"))
    passport_number = models.CharField(max_length=255, blank=True, verbose_name=_("passport_number"))
    marital_status = models.CharField(max_length=255, blank=True, choices=MARITAL_STATUS_CHOICES,
                                      verbose_name=_("marital_status"))
    spouse_name = models.CharField(max_length=255, blank=True, verbose_name=_("spouse_name"))
    children_number = models.SmallIntegerField(blank=True, default=0, verbose_name=_("children_number"))
    previous_ucl_registration = models.BooleanField(default=False, verbose_name=_("previous_ucl_registration"))
    previous_noma = models.CharField(max_length=255, blank=True, verbose_name=_("previous_noma"))

    #Post
    use_address_for_post = models.BooleanField(default=False, verbose_name=_("use_address_for_post"))
    residence_address = models.ForeignKey('continuing_education.Address', blank=True, null=True,
                                          related_name="residence_address", verbose_name=_("residence_address"))

    residence_phone = models.CharField(max_length=30, blank=True, verbose_name=_("residence_phone"))

    #Student Sheet
    registration_complete = models.BooleanField(default=False, verbose_name=_("registration_complete"))
    noma = models.CharField(max_length=255, blank=True, verbose_name=_("noma"))
    payment_complete = models.BooleanField(default=False, verbose_name=_("payment_complete"))
    formation_spreading = models.BooleanField(default=False, verbose_name=_("formation_spreading"))
    prior_experience_validation = models.BooleanField(default=False, verbose_name=_("prior_experience_validation"))
    assessment_presented = models.BooleanField(default=False, verbose_name=_("assessment_presented"))
    assessment_succeeded = models.BooleanField(default=False, verbose_name=_("assessment_succeeded"))
    #ajouter dates sessions cours suivies
    sessions = models.CharField(max_length=255, blank=True, verbose_name=_("sessions"))


def find_by_id(a_id):
    try:
        return Admission.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return None

#à modifier lors du lien avec une table student
def find_by_person(person):
    return Admission.objects.filter(person_information=person)


def find_by_state(state):
    return Admission.objects.filter(state=state)
