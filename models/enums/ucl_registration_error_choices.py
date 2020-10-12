from django.utils.translation import gettext_lazy as _

from base.models.utils.utils import ChoiceEnum


class UCLRegistrationError(ChoiceEnum):
    IUFC_NO_ERROR = _('No error')
    IUFC_NOM_TROP_LONG = _('Too long name')
    IUFC_PRENOM_TROP_LONG = _('Too long first name')
    IUFC_ADRESSE_TROP_LONGUE = _('Too long address')
    IUFC_NOM_MANQUANT = _('Missing name')
    IUFC_PRENOM_MANQUANT = _('Missing first name')
    IUFC_ANNEE_MANQUANTE = _('Missing year')
    IUFC_PROGRAMME_MANQUANT = _('Missing program')
    IUFC_NATIONALITE_MANQUANTE = _('Missing citizenship')
    IUFC_PAYS_NAISSANCE_MANQUANT = _('Missing birth country')
    IUFC_INSCRIPTION_DEJA_TRAITEE = _('Registration already processed')
    IUFC_CREATION_NOMA_ECHOUEE = _('NOMA creation failed')
    IUFC_ERREUR_INCONNUE = _('Unknown error: please contact Service Desk for further help')
