from rules import predicate

from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.person_training import PersonTraining
from continuing_education.models.prospect import Prospect


@predicate(bind=True)
def is_admission_draft(self, user, admission):
    return admission and admission.is_draft()


@predicate(bind=True)
def is_registration_submitted(self, user, registration):
    return registration.is_registration_submitted()


@predicate(bind=True)
def is_new_instance(self, user, admission):
    return admission.id is None


@predicate(bind=True)
def is_training_manager(self, user, obj):
    person_trainings = PersonTraining.objects.filter(person=user.person).values_list('training', flat=True)
    if isinstance(obj, (Admission, Prospect)):
        return obj.formation.id in person_trainings
    if isinstance(obj, ContinuingEducationTraining):
        return obj.id in person_trainings
    return None
