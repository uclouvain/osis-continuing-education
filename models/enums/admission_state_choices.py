from django.utils.translation import gettext_lazy as _

ACCEPTED = 'Accepted'
ACCEPTED_NO_REGISTRATION_REQUIRED = 'Accepted (no registration required)'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'
REGISTRATION_SUBMITTED = 'Registration submitted'
VALIDATED = 'Validated'

CANCELLED = 'Cancelled'
CANCELLED_NO_REGISTRATION_REQUIRED = "Cancelled (no registration required)"

STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (ACCEPTED_NO_REGISTRATION_REQUIRED, _('Accepted (no registration required)')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
    (VALIDATED, _('Validated')),
    (CANCELLED, _('Cancelled')),
    (CANCELLED_NO_REGISTRATION_REQUIRED, _('Cancelled (no registration required)')),
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
    'states': [
        ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED,
        REJECTED, WAITING, DRAFT, CANCELLED, CANCELLED_NO_REGISTRATION_REQUIRED
    ]
}

STATES_ACCEPTED_VALIDATED = {
    'choices': (
        (REGISTRATION_SUBMITTED, _('Registration submitted')),
        (CANCELLED, _('Cancelled')),
    ),
    'states': [REGISTRATION_SUBMITTED, CANCELLED]
}

STATES_ACCEPTED_NO_REGISTRATION_REQUIRED = {
    'choices': (
        (CANCELLED_NO_REGISTRATION_REQUIRED, _('Cancelled')),
    ),
    'states': [CANCELLED_NO_REGISTRATION_REQUIRED]
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
    'states': [
        ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED,
        REJECTED, WAITING, CANCELLED, CANCELLED_NO_REGISTRATION_REQUIRED
    ]
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
    'states': [
        ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED,
        REJECTED, WAITING, VALIDATED, REGISTRATION_SUBMITTED, DRAFT, SUBMITTED
    ]
}

STATES_CANCELLED_NO_REGISTRATION_REQUIRED = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (DRAFT, _('Draft')),
        (WAITING, _('Waiting')),
        (REJECTED, _('Rejected')),
        (SUBMITTED, _('Submitted')),
    ),
    'states': [ACCEPTED, ACCEPTED_NO_REGISTRATION_REQUIRED, REJECTED, WAITING, DRAFT, SUBMITTED]
}

NEW_ADMIN_STATE = {
    DRAFT: STATES_DRAFT,
    SUBMITTED: STATES_SUBMITTED,
    WAITING: STATES_REJECTED_WAITING,
    ACCEPTED: STATES_ACCEPTED_VALIDATED,
    REJECTED: STATES_REJECTED_WAITING,
    VALIDATED: STATES_ACCEPTED_VALIDATED,
    REGISTRATION_SUBMITTED: STATES_REGISTRATION_SUBMITTED,
    CANCELLED: STATES_CANCELLED,
    ACCEPTED_NO_REGISTRATION_REQUIRED: STATES_ACCEPTED_NO_REGISTRATION_REQUIRED,
    CANCELLED_NO_REGISTRATION_REQUIRED: STATES_CANCELLED_NO_REGISTRATION_REQUIRED
}

ADMISSION_STATE_CHOICES = (
    (SUBMITTED, _('Submitted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (ACCEPTED_NO_REGISTRATION_REQUIRED, _('Accepted'))
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

REGISTRATION_STATE_CHOICES_FOR_CONTINUING_EDUCATION_MGR = (
    (ACCEPTED, _('Accepted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
)
