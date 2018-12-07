from django.db.models.signals import post_save
from django.dispatch import receiver
from continuing_education.models.admission import Admission


@receiver(post_save, sender=Admission)
def admission_update_callback(sender, instance, created, **kwargs):
    print('Admission from {} {} for {} saved!'.format(
        instance.person_information.person.last_name,
        instance.person_information.person.first_name,
        instance.formation
    ))