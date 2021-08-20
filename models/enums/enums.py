from django.utils.translation import gettext_lazy as _

YES_NO_CHOICES = (
    (False, _('No')),
    (True, _('Yes'))
)

REGISTRATION_TITLE_CHOICES = (
    ('PRIVATE', _('Private')),
    ('PROFESSIONAL', _('Professional')),
)

MARITAL_STATUS_CHOICES = (
    ('SINGLE', _('Single')),
    ('MARRIED', _('Married')),
    ('WIDOWED', _('Widowed')),
    ('DIVORCED', _('Divorced')),
    ('SEPARATED', _('Separated')),
    ('LEGAL_COHABITANT', _('Legal cohabitant')),
)

GENDER_CHOICES = (
    ('F', _('Female')),
    ('H', _('Male')),
)

STATUS_CHOICES = (
    ('EMPLOYEE', _('Employee')),
    ('SELF_EMPLOYED', _('Self employed')),
    ('JOB_SEEKER', _('Job seeker')),
    ('PUBLIC_SERVANT', _('Public servant')),
    ('OTHER', _('Other')),
)

SECTOR_CHOICES = (
    ('PRIVATE', _('Private')),
    ('PUBLIC', _('Public')),
    ('ASSOCIATIVE', _('Associative')),
    ('HEALTH', _('Health')),
    ('OTHER', _('Other')),
)
