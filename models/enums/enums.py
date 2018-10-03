from django.utils.translation import ugettext_lazy as _

YES_NO_CHOICES = (
    (False, _('No')),
    (True, _('Yes'))
)

REGISTRATION_TITLE_CHOICES = (
    ('PRIVATE', _('private')),
    ('PROFESSIONAL', _('professional')),
)

MARITAL_STATUS_CHOICES = (
    ('SINGLE', _('single')),
    ('MARRIED', _('married')),
    ('WIDOWED', _('widowed')),
    ('DIVORCED', _('divorced')),
    ('SEPARATED', _('separated')),
    ('LEGAL_COHABITANT', _('legal_cohabitant')),
)

STATE_CHOICES = (
    ('accepted', _('accepted')),
    ('rejected', _('rejected')),
    ('waiting', _('waiting')),
)

GENDER_CHOICES = (
    ('F', _('female')),
    ('M', _('male')),
)

STATUS_CHOICES = (
    ('EMPLOYEE', _('employee')),
    ('SELF_EMPLOYED', _('self_employed')),
    ('JOB_SEEKER', _('job_seeker')),
    ('PUBLIC_SERVANT', _('public_servant')),
    ('OTHER', _('other')),
)

SECTOR_CHOICES = (
    ('PRIVATE', _('private')),
    ('PUBLIC', _('public')),
    ('ASSOCIATIVE', _('associative')),
    ('HEALTH', _('health')),
    ('OTHER', _('other')),
)
