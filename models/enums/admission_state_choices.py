from django.utils.translation import ugettext_lazy as _

ACCEPTED = 'Accepted'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'
REGISTRATION_SUBMITTED = 'Registration submitted'

STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (SUBMITTED, _('Submitted')),
    (REGISTRATION_SUBMITTED, _('Registration submitted')),
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
STATES_ADMIN = {
    'choices': (
        (ACCEPTED, _('Accepted')),
        (REJECTED, _('Rejected')),
        (WAITING, _('Waiting')),
    ),
    'states': [ACCEPTED, REJECTED, WAITING, REGISTRATION_SUBMITTED]
}

NEW_ADMIN_STATE = {
    DRAFT: STATES_DRAFT,
    SUBMITTED: STATES_SUBMITTED,
    WAITING: STATES_ADMIN,
    ACCEPTED: STATES_ADMIN,
    REJECTED: STATES_ADMIN,
}
