from django.utils.translation import gettext_lazy as _

INIT_STATE = 'Initial state'
SENDED = 'Sended'
REGISTERED = 'Registered'
ON_DEMAND = 'On demand'
REJECTED = 'Rejected'

STATE_CHOICES = (
    (INIT_STATE, _('Initial state')),
    (SENDED, _('Sended')),
    (REGISTERED, _('Registered')),
    (ON_DEMAND, _('On demand')),
    (REJECTED, _('Rejected'))
)
