import rules
from django.db import models
from django.utils.translation import gettext_lazy as _

from continuing_education.auth.predicates import is_user_linked_to_training, is_admission_draft, is_new_instance, \
    is_user_linked_to_admission, is_user_linked_to_prospect
from continuing_education.models.enums.groups import TRAINING_MANAGERS_GROUP
from osis_common.models.osis_model_admin import OsisModelAdmin
from osis_role.contrib import models as osis_role_models


class ContinuingEducationTrainingManagerAdmin(OsisModelAdmin):
    list_display = ('person', 'training',)


class ContinuingEducationTrainingManager(osis_role_models.RoleModel):
    class Meta:
        verbose_name = _("Continuing education training manager")
        verbose_name_plural = _("Continuing education training managers")
        group_name = "continuing_education_training_managers"
        unique_together = ("person", "training")
        default_permissions = ['view', 'add', 'delete']

    training = models.ForeignKey(
        'continuing_education.ContinuingEducationTraining',
        null=True,
        on_delete=models.CASCADE
    )

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'continuing_education.view_admission': is_user_linked_to_admission,
            'continuing_education.change_admission': is_user_linked_to_admission & ~is_admission_draft,
            'continuing_education.archive_admission': is_user_linked_to_admission,
            'continuing_education.cancel_admission': is_user_linked_to_admission,
            'continuing_education.export_admission': is_user_linked_to_admission,
            'continuing_education.change_received_file_state': is_user_linked_to_admission,
            'continuing_education.link_admission_to_academic_year': is_new_instance | is_user_linked_to_admission,
            'continuing_education.send_notification': is_user_linked_to_admission,
            'continuing_education.view_continuingeducationtraining': is_user_linked_to_training,
            'continuing_education.change_continuingeducationtraining': is_user_linked_to_training,
            'continuing_education.view_prospect': is_user_linked_to_prospect,
            'continuing_education.export_prospect': is_user_linked_to_prospect,
            'continuing_education.change_admission_state': is_user_linked_to_admission,
            'continuing_education.view_admission_archives': is_user_linked_to_admission,
            'continuing_education.cancel_draft': is_user_linked_to_admission,
            'continuing_education.delete_prospect': is_user_linked_to_prospect,
        })


def is_continuing_education_training_manager(user):
    return user.groups.filter(name=TRAINING_MANAGERS_GROUP).exists()
