from django.utils.translation import ugettext_lazy as _

ACCEPTED = 'Accepted'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'
REGISTRATION_SUBMITTED = 'Registration submitted'
VALIDATED = 'Validated'

CANCELLED = 'Cancelled'

STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
    (CANCELLED, _('Cancelled')),
)

STATES_DRAFT = {
    'choices': ((SUBMITTED, _('Submitted')),
                (CANCELLED, _('Cancelled')),
                ),
    'states': [SUBMITTED, CANCELLED]
}
STATES_SUBMITTED = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (WAITING, _('Waiting')),
        (DRAFT, _('Draft')),
        (CANCELLED, _('Cancelled')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING, DRAFT, CANCELLED]
}

STATES_ACCEPTED_VALIDATED = {
    'choices': (
        (REGISTRATION_SUBMITTED, _('Registration submitted')),
        (CANCELLED, _('Cancelled')),
    ),
    'states': [REGISTRATION_SUBMITTED, CANCELLED]
}

STATES_REGISTRATION_SUBMITTED = {
    'choices': (
        (VALIDATED, _('Validated')),
        (CANCELLED, _('Cancelled')),
    ),
    'states': [VALIDATED, CANCELLED]
}

STATES_REJECTED_WAITING = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (WAITING, _('Waiting')),
        (CANCELLED, _('Cancelled')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING, CANCELLED]
}

STATES_CANCELLED = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (DRAFT, _('Draft')),
        (WAITING, _('Waiting')),
        (REGISTRATION_SUBMITTED, _('Registration submitted')),
        (REJECTED, _('Rejected')),
        (SUBMITTED, _('Submitted')),
        (VALIDATED, _('Validated')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING, VALIDATED, REGISTRATION_SUBMITTED, DRAFT, SUBMITTED]
}

NEW_ADMIN_STATE = {
    DRAFT: STATES_DRAFT,
    SUBMITTED: STATES_SUBMITTED,
    WAITING: STATES_REJECTED_WAITING,
    ACCEPTED: STATES_ACCEPTED_VALIDATED,
    REJECTED: STATES_REJECTED_WAITING,
    VALIDATED: STATES_ACCEPTED_VALIDATED,
    REGISTRATION_SUBMITTED: STATES_REGISTRATION_SUBMITTED,
    CANCELLED: STATES_CANCELLED
}

ADMISSION_STATE_CHOICES = (
    (SUBMITTED, _('Submitted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (CANCELLED, _('Cancelled')),
)
REGISTRATION_STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
    (CANCELLED, _('Cancelled')),
)

ARCHIVE_STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
)
