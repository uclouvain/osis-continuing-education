from datetime import datetime

from django.contrib.admin import ModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from base.models.academic_year import current_academic_years
from base.models.enums import entity_type


class AdmissionAdmin(ModelAdmin):
    list_display = ('person', 'formation')

class Admission(models.Model):

    CONTINUING_EDUCATION_TYPE = 8

    REGISTRATION_TITLE_CHOICES = (
        ('PRIVATE', _('private')),
        ('PROFESSIONAL', _('professional')),
    )

    MARITAL_STATUS_CHOICES = (
        ('SINGLE', _('single')),
        ('MARRIED', _('married')),
        ('WIDOWED', _('widowed')),
        ('DIVORCED', _('divorced')),
        ('SEPARATED', _('separated')),
        ('LEGAL_COHABITANT', _('legal_cohabitant')),
    )

    STATE_CHOICES = (
        ('accepted', _('accepted')),
        ('rejected', _('rejected')),
        ('waiting', _('waiting')),
    )

    person = models.ForeignKey('continuing_education.Person', blank=True, null=True)

    #Motivation
    motivation = models.TextField(blank=True)
    professional_impact = models.TextField(blank=True)

    #Formation
    formation = models.ForeignKey('base.OfferYear',
                                        limit_choices_to={
                                            'offer_type_id': CONTINUING_EDUCATION_TYPE,
                                            'academic_year_id': current_academic_years()
                                        },
                                        blank=True, null=True)
    faculty = models.ForeignKey('base.EntityVersion',
                                        limit_choices_to={
                                            'entity_type': entity_type.FACULTY,
                                        },
                                        blank=True, null=True)

    #Awareness
    awareness_ucl_website = models.BooleanField(default=False)
    awareness_formation_website = models.BooleanField(default=False)
    awareness_press = models.BooleanField(default=False)
    awareness_facebook = models.BooleanField(default=False)
    awareness_linkedin = models.BooleanField(default=False)
    awareness_customized_mail = models.BooleanField(default=False)
    awareness_emailing = models.BooleanField(default=False)

    #State
    state = models.CharField(max_length=50, blank=True,  choices=STATE_CHOICES)

    #Billing
    registration_type = models.CharField(max_length=50, blank=True, choices=REGISTRATION_TITLE_CHOICES)
    use_address_for_billing = models.BooleanField(default=False)
    billing_address = models.ForeignKey('continuing_education.Address', blank=True, null=True, related_name="billing_address")

    head_office_name = models.CharField(max_length=255, blank=True)
    company_number = models.CharField(max_length=255, blank=True)
    vat_number = models.CharField(max_length=255, blank=True)

    #Registration
    national_registry_number = models.CharField(max_length=255, blank=True)
    id_card_number = models.CharField(max_length=255, blank=True)
    passport_number = models.CharField(max_length=255, blank=True)
    marital_status = models.CharField(max_length=255, blank=True, choices=MARITAL_STATUS_CHOICES)
    spouse_name = models.CharField(max_length=255, blank=True)
    children_number = models.SmallIntegerField(blank=True, default=0)
    previous_ucl_registration = models.BooleanField(default=False)
    previous_noma = models.CharField(max_length=255, blank=True)

    #Post
    use_address_for_post = models.BooleanField(default=False)
    residence_address = models.ForeignKey('continuing_education.Address', blank=True, null=True, related_name="residence_address")

    residence_phone = models.CharField(max_length=30, blank=True)

    #Student Sheet
    registration_complete = models.BooleanField(default=False)
    noma = models.CharField(max_length=255, blank=True)
    payment_complete = models.BooleanField(default=False)
    formation_spreading = models.BooleanField(default=False)
    prior_experience_validation = models.BooleanField(default=False)
    assessment_presented = models.BooleanField(default=False)
    assessment_succeeded = models.BooleanField(default=False)
    #ajouter dates sessions cours suivies
    sessions = models.CharField(max_length=255, blank=True)

def find_by_id(a_id):
    try:
        return Admission.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return None

#à modifier lors du lien avec une table student
def find_by_person(person):
        return Admission.objects.filter(person=person)