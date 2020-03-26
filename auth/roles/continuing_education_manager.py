import rules
from django.utils.translation import gettext_lazy as _

from continuing_education.auth import predicates
from osis_common.models.osis_model_admin import OsisModelAdmin
from osis_role.contrib import models as osis_role_models


class ContinuingEducationManagerAdmin(OsisModelAdmin):
    list_display = ('person',)


class ContinuingEducationManager(osis_role_models.RoleModel):
    class Meta:
        verbose_name = _("Continuing education manager")
        verbose_name_plural = _("Continuing education managers")
        group_name = "continuing_education_managers"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'continuing_education.view_admission': rules.always_allow,
            'continuing_education.change_admission': ~predicates.is_admission_draft,
            'continuing_education.validate_registration': predicates.is_registration_submitted,
            'continuing_education.view_persontraining': rules.always_allow,
            'continuing_education.add_persontraining': rules.always_allow,
            'continuing_education.delete_persontraining': rules.always_allow,
        })
