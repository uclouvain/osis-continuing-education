from rules import predicate


@predicate(bind=True)
def is_admission_draft(self, user, admission):
    return admission and admission.is_draft()


@predicate(bind=True)
def is_registration_submitted(self, user, registration):
    return registration.is_registration_submitted()
