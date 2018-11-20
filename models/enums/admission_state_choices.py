from django.utils.translation import ugettext_lazy as _

ACCEPTED = 'Accepted'
REJECTED = 'Rejected'
WAITING = 'Waiting'

DRAFT = 'Draft'
SUBMITTED = 'Submitted'

ADMIN_STATE_CHOICES = (
    (ACCEPTED, _(ACCEPTED)),
    (REJECTED, _(REJECTED)),
    (WAITING, _(WAITING)),
)

STUDENT_STATE_CHOICES = (
    (DRAFT, _(DRAFT)),
    (SUBMITTED, _(SUBMITTED)),
)

STATE_CHOICES = ADMIN_STATE_CHOICES + STUDENT_STATE_CHOICES
