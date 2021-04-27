import rules
from django.utils.translation import gettext_lazy as _

from continuing_education.auth.predicates import is_admission_draft, is_registration_submitted
from continuing_education.models.enums.groups import MANAGERS_GROUP
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
            'continuing_education.change_admission': ~is_admission_draft,
            'continuing_education.archive_admission': rules.always_allow,
            'continuing_education.cancel_admission': rules.always_allow,
            'continuing_education.export_admission': rules.always_allow,
            'continuing_education.validate_registration': is_registration_submitted,
            'continuing_education.view_continuingeducationtrainingmanager': rules.always_allow,
            'continuing_education.add_continuingeducationtrainingmanager': rules.always_allow,
            'continuing_education.delete_continuingeducationtrainingmanager': rules.always_allow,
            'continuing_education.change_received_file_state': rules.always_allow,
            'continuing_education.link_admission_to_academic_year': rules.always_allow,
            'continuing_education.manage_all_trainings': rules.always_allow,
            'continuing_education.inject_admission_to_epc': rules.always_allow,
            'continuing_education.set_training_active': rules.always_allow,
            'continuing_education.mark_diploma_produced': rules.always_allow,
            'continuing_education.send_notification': rules.always_allow,
            'continuing_education.view_continuingeducationtraining': rules.always_allow,
            'continuing_education.change_continuingeducationtraining': rules.always_allow,
            'continuing_education.view_prospect': rules.always_allow,
            'continuing_education.export_prospect': rules.always_allow,
            'continuing_education.view_admission_archives': rules.always_allow,
            'continuing_education.change_admission_state': rules.always_allow,
        })


def is_continuing_education_manager(user):
    return user.groups.filter(name=MANAGERS_GROUP).exists()
