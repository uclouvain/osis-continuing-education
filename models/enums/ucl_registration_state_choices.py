from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum


class UCLRegistrationState(ChoiceEnum):
    INIT_STATE = _('Initial state')
    SENDED = _('Sended')
    INSCRIT = _('Registered')
    DEMANDE = _('On demand')
    REJECTED = _('Rejected')
    NON_RENSEIGNE = _("Uninformed")
    CONDITION = _("Provisional")
    ANNULATION_ETD = _("Cancellation (ETD)")
    ANNULATION_UCL = _("Cancellation (UNIV)")
    EXCLUSION = _("Exclusion")
    CESSATION = _("Cessation")
    DECES = _("Death")
    ERREUR = _("Error")
    INTENTION_ECHANGE = _("Register intention")
    ANNULATION_ECHANGE = _("Intention cancellation")
    REINSCRIPTION_WEB = _("Internet re-registration")
    ANNULATION_IP = _("IP Cancellation")
    REFUS = _("Refusal")
    CYCLE = _("Cycle")
    VALISE_CREDITS = _("Valued crédits")
