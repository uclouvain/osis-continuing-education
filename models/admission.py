from django.contrib.admin import ModelAdmin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

class AdmissionAdmin(ModelAdmin):
    list_display = ('last_name', 'first_name','country','formation_title', 'program_code')

class Admission(models.Model):

    GENDER_CHOICES = (
        ('F', _('female')),
        ('M', _('male')),
        ('U', _('unknown'))
    )

    STATUS_CHOICES = (
        ('EMPLOYEE', _('employee')),
        ('SELF_EMPLOYED', _('self_employed')),
        ('JOB_SEEKER', _('job_seeker')),
        ('PUBLIC_SERVANT', _('public_servant'))
    )
    #Identification
    first_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_location =  models.CharField(max_length=255, blank=True, null=True)
    birth_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='birth_country')
    citizenship = models.ForeignKey('reference.Country', blank=True, null=True, related_name='citizenship')
    gender = models.CharField(max_length=1, blank=True, null=True, choices=GENDER_CHOICES, default='U')

    #Contact
    phone_mobile = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    #Address
    location = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='address_country')

    #Education
    high_school_diploma = models.BooleanField(default=False)
    high_school_graduation_year = models.DateField(blank=True, null=True)
    last_degree_level = models.CharField(max_length=50, blank=True, null=True)
    last_degree_field = models.CharField(max_length=50, blank=True, null=True)
    last_degree_institution = models.CharField(max_length=50, blank=True, null=True)
    last_degree_graduation_year = models.DateField(blank=True, null=True)
    other_educational_background = models.TextField(blank=True, null=True)

    #Professional Background
    professional_status = models.CharField(max_length=50, blank=True, null=True, choices=STATUS_CHOICES)
    current_occupation = models.CharField(max_length=50, blank=True, null=True)
    current_employer = models.CharField(max_length=50, blank=True, null=True)
    activity_sector = models.CharField(max_length=50, blank=True, null=True)
    past_professional_activities = models.TextField(blank=True, null=True)

    #Motivation
    motivation = models.TextField(blank=True, null=True)
    professional_impact = models.TextField(blank=True, null=True)

    #Formation
    formation_title = models.CharField(max_length=50, blank=True, null=True)
    courses_formula = models.CharField(max_length=50, blank=True, null=True)
    program_code = models.CharField(max_length=50, blank=True, null=True)
    faculty = models.CharField(max_length=50, blank=True, null=True)
    formation_administrator = models.CharField(max_length=50, blank=True, null=True)

    #Awareness
    ucl_website = models.BooleanField(default=False)
    formation_website = models.BooleanField(default=False)
    press = models.BooleanField(default=False)
    facebook = models.BooleanField(default=False)
    linkedin = models.BooleanField(default=False)
    customized_mail = models.BooleanField(default=False)
    emailing = models.BooleanField(default=False)

    #State
    state = models.CharField(max_length=50, blank=True, null=True)

    #Billing
    registration_type = models.CharField(max_length=50, blank=True, null=True)
    use_address_for_billing = models.BooleanField(default=False)
    billing_location = models.CharField(max_length=255, blank=True, null=True)
    billing_postal_code = models.CharField(max_length=20, blank=True, null=True)
    billing_city = models.CharField(max_length=255, blank=True, null=True)
    billing_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='billing_country')
    head_office_name = models.CharField(max_length=255, blank=True, null=True)
    company_number = models.CharField(max_length=255, blank=True, null=True)
    vat_number = models.CharField(max_length=255, blank=True, null=True)

    #Registration
    national_registry_number = models.CharField(max_length=255, blank=True, null=True)
    id_card_number = models.CharField(max_length=255, blank=True, null=True)
    passport_number = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=255, blank=True, null=True)
    spouse_name = models.CharField(max_length=255, blank=True, null=True)
    children_number = models.SmallIntegerField(blank=True, null=True)
    previous_ucl_registration = models.BooleanField(default=False)
    previous_noma = models.CharField(max_length=255, blank=True, null=True)

    #Post
    use_address_for_post = models.BooleanField(default=False)
    residence_location = models.CharField(max_length=255, blank=True, null=True)
    residence_postal_code = models.CharField(max_length=20, blank=True, null=True)
    residence_city = models.CharField(max_length=255, blank=True, null=True)
    residence_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='residence_country')
    residence_phone = models.CharField(max_length=30, blank=True, null=True)

    #Student Sheet
    registration_complete = models.BooleanField(default=False)
    noma = models.CharField(max_length=255, blank=True, null=True)
    payment_complete = models.BooleanField(default=False)
    formation_spreading = models.BooleanField(default=False)
    prior_experience_validation = models.BooleanField(default=False)
    assessment_presented = models.BooleanField(default=False)
    assessment_succeded = models.BooleanField(default=False)
    #ajouter dates sessions cours suivies
    sessions = models.CharField(max_length=255, blank=True, null=True)


def find_by_id(a_id):
    try:
        return Admission.objects.get(pk=a_id)
    except ObjectDoesNotExist:
        return None

#à modifier lors du lien avec une table student
def find_by_student(first_name, last_name):
        return Admission.objects.filter(first_name=first_name, last_name=last_name)