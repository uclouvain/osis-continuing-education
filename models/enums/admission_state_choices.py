from django.utils.translation import ugettext_lazy as _

ACCEPTED = 'Accepted'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'

STATE_CHOICES = (
    (ACCEPTED, _('Accepted')),
    (REJECTED, _('Rejected')),
    (WAITING, _('Waiting')),
    (DRAFT, _('Draft')),
    (SUBMITTED, _('Submitted')),
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
    'states': [ACCEPTED, REJECTED, WAITING]
}

NEW_ADMIN_STATE = {
    DRAFT: STATES_DRAFT,
    SUBMITTED: STATES_SUBMITTED,
    WAITING: STATES_ADMIN,
    ACCEPTED: STATES_ADMIN,
    REJECTED: STATES_ADMIN,
}