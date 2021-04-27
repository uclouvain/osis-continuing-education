from rules import predicate


@predicate(bind=True)
def is_admission_draft(self, user, admission):
    return admission and admission.is_draft()


@predicate(bind=True)
def is_registration_submitted(self, user, registration):
    return registration.is_registration_submitted()


@predicate(bind=True)
def is_registration_validated(self, user, registration):
    return registration.is_validated()


@predicate(bind=True)
def is_new_instance(self, user, admission):
    return admission.id is None


@predicate(bind=True)
def is_user_linked_to_training(self, user, training):
    if training:
        return self.context['role_qs'].filter(training=training).exists()


@predicate(bind=True)
def is_user_linked_to_admission(self, user, admission):
    if admission:
        return self.context['role_qs'].filter(training=admission.formation).exists()


@predicate(bind=True)
def is_user_linked_to_prospect(self, user, prospect):
    if prospect:
        return self.context['role_qs'].filter(training=prospect.formation).exists()
