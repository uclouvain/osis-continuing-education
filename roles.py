from continuing_education.auth.roles import continuing_education_manager, continuing_education_student_worker, \
    continuing_education_training_manager
from osis_role import role

role.role_manager.register(continuing_education_manager.ContinuingEducationManager)
role.role_manager.register(continuing_education_student_worker.ContinuingEducationStudentWorker)
role.role_manager.register(continuing_education_training_manager.ContinuingEducationTrainingManager)
