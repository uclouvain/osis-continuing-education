from datetime import datetime

from django.contrib.admin import ModelAdmin
from django.db import models
from django.utils.translation import ugettext_lazy as _

from continuing_education.models.enums.enums import STATUS_CHOICES, SECTOR_CHOICES
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class ContinuingEducationPersonAdmin(SerializableModelAdmin):
    list_display = ('person', 'citizenship', 'email',)
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ('activity_sector', 'citizenship')

class ContinuingEducationPerson(SerializableModel):

    person = models.OneToOneField('base.Person', on_delete=models.CASCADE)

    birth_date = models.DateField(blank=True, default=datetime.now, verbose_name=_("birth_date"))

    birth_location = models.CharField(max_length=255, blank=True, verbose_name=_("birth_location"))
    birth_country = models.ForeignKey('reference.Country', blank=True, null=True, related_name='birth_country',
                                      verbose_name=_("birth_country"))
    citizenship = models.ForeignKey('reference.Country', blank=True, null=True, related_name='citizenship',
                                    verbose_name=_("citizenship"))
    # Contact
    address = models.ForeignKey('continuing_education.Address', blank=True, null=True, verbose_name=_("address"))
    phone_mobile = models.CharField(max_length=30, blank=True,  verbose_name=_("phone_mobile"))
    email = models.EmailField(max_length=255, blank=True,  verbose_name=_("email"))

    # Education
    high_school_diploma = models.BooleanField(default=False, verbose_name=_("high_school_diploma"))
    high_school_graduation_year = models.DateField(blank=True, default=datetime.now,
                                                   verbose_name=_("high_school_graduation_year"))
    last_degree_level = models.CharField(max_length=50, blank=True, verbose_name=_("last_degree_level"))
    last_degree_field = models.CharField(max_length=50, blank=True, verbose_name=_("last_degree_field"))
    last_degree_institution = models.CharField(max_length=50, blank=True, verbose_name=_("last_degree_institution"))
    last_degree_graduation_year = models.DateField(blank=True, default=datetime.now,
                                                   verbose_name=_("last_degree_graduation_year"))
    other_educational_background = models.TextField(blank=True, verbose_name=_("other_educational_background"))

    # Professional Background
    professional_status = models.CharField(max_length=50, blank=True, choices=STATUS_CHOICES,
                                           verbose_name=_("professional_status"))
    current_occupation = models.CharField(max_length=50, blank=True, verbose_name=_("current_occupation"))
    current_employer = models.CharField(max_length=50, blank=True, verbose_name=_("current_employer"))
    activity_sector = models.CharField(max_length=50, blank=True, choices=SECTOR_CHOICES,
                                       verbose_name=_("activity_sector"))
    past_professional_activities = models.TextField(blank=True, verbose_name=_("past_professional_activities"))

    def __str__(self):
        return "{} - {} {} - {}".format(self.id, self.person.first_name, self.person.last_name, self.person.email)


def find_by_person(person):
    return ContinuingEducationPerson.objects.filter(person=person).first()
