from django.utils.translation import ugettext_lazy as _

ACCEPTED = 'Accepted'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'
REGISTRATION_SUBMITTED = 'Registration submitted'
VALIDATED = 'Validated'

STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
)

STATES_DRAFT = {
    'choices': ((SUBMITTED, _('Submitted')),),
    'states': [SUBMITTED]
}
STATES_SUBMITTED = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (WAITING, _('Waiting')),
        (DRAFT, _('Draft')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING, DRAFT]
}

STATES_ACCEPTED_VALIDATED = {
    'choices': (
        (REGISTRATION_SUBMITTED, _('Registration submitted')),
    ),
    'states': [REGISTRATION_SUBMITTED]
}

STATES_REGISTRATION_SUBMITTED = {
    'choices': (
        (VALIDATED, _('Validated')),
    ),
    'states': [VALIDATED]
}

STATES_REJECTED_WAITING = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (WAITING, _('Waiting')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING]
}

NEW_ADMIN_STATE = {
    DRAFT: STATES_DRAFT,
    SUBMITTED: STATES_SUBMITTED,
    WAITING: STATES_REJECTED_WAITING,
    ACCEPTED: STATES_ACCEPTED_VALIDATED,
    REJECTED: STATES_REJECTED_WAITING,
    VALIDATED: STATES_ACCEPTED_VALIDATED,
    REGISTRATION_SUBMITTED: STATES_REGISTRATION_SUBMITTED
}

ADMISSION_STATE_CHOICES = (
    (SUBMITTED, _('Submitted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
)
REGISTRATION_STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
)

ARCHIVE_STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
)
