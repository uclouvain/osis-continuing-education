import rules
from django.utils.translation import gettext_lazy as _

from continuing_education.auth import predicates
from continuing_education.models.enums.groups import STUDENT_WORKERS_GROUP
from osis_common.models.osis_model_admin import OsisModelAdmin
from osis_role.contrib import models as osis_role_models


class ContinuingEducationStudentWorkerAdmin(OsisModelAdmin):
    list_display = ('person',)


class ContinuingEducationStudentWorker(osis_role_models.RoleModel):
    class Meta:
        verbose_name = _("Continuing education student worker")
        verbose_name_plural = _("Continuing education student worker")
        group_name = "continuing_education_student_workers"

    @classmethod
    def rule_set(cls):
        return rules.RuleSet({
            'continuing_education.view_admission': rules.always_allow,
            'continuing_education.validate_registration': predicates.is_registration_submitted,
            'continuing_education.change_received_file_state': rules.always_allow,
        })


def is_continuing_education_student_worker(user):
    return user.groups.filter(name=STUDENT_WORKERS_GROUP).exists()