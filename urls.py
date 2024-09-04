##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.conf.urls import include
from django.urls import path

import continuing_education.views.file
from continuing_education.business import registration_queue
from continuing_education.views import (home, admission, registration, archive, formation, prospect, tasks, managers)
from continuing_education.views.autocomplete.continuing_education_training import \
    ContinuingEducationTrainingAutocomplete

urlpatterns = [
    path('', home.main_view, name='continuing_education'),
    path('admission/', include([
        path('', admission.list_admissions, name='admission'),
        path('new/', admission.admission_form, name='admission_new'),
        path('edit/<int:admission_id>/', admission.admission_form, name='admission_edit'),
        path('delete_draft/', admission.delete_draft, name='admission_delete_draft'),
        path('<int:admission_id>/', include([
            path('', admission.admission_detail, name='admission_detail'),
            path('send_invoice_notification_mail/', admission.send_invoice_notification_mail,
                 name='send_invoice_notification_mail'),
            path('file/<int:file_id>', continuing_education.views.file.download_file, name='download_file'),
            path('file/<int:file_id>/delete', continuing_education.views.file.delete_file, name='delete_file'),
        ])),
        path('validate_field/<int:admission_id>/', admission.validate_field, name='validate_field'),
        path('ajax/formation/', admission.get_formation_information, name='get_formation_information'),
        path('billing_edit/<int:admission_id>/', admission.billing_edit, name='billing_edit'),
    ])),
    path('registration/', include([
        path('', registration.list_registrations, name='registration'),
        path('edit/<int:admission_id>/', registration.registration_edit, name='registration_edit'),
        path('list/receive_files/', registration.receive_files_procedure, name='receive_files_procedure'),
        path('change_received_file_state/<int:admission_id>/', registration.receive_file_procedure,
             name='receive_file_procedure'),
        path('cancelled/', registration.list_cancelled, name='cancelled_files'),
    ])),
    path('archive/', include([
        path('', archive.list_archives, name='archive'),
        path('list/to_archive/', archive.archives_procedure, name='archives_procedure'),
        path('list/to_unarchive/', archive.unarchives_procedure, name='unarchives_procedure'),
        path('to_archive/<int:admission_id>/', archive.archive_procedure, name='archive_procedure'),
    ])),
    path('formation/', include([
        path('', formation.list_formations, name='formation'),
        path('list/update/', formation.update_formations, name='update_formations'),
        path('<int:formation_id>/', formation.formation_detail, name='formation_detail'),
        path('edit/<int:formation_id>/', formation.formation_edit, name='formation_edit'),
    ])),
    path('prospects/', include([
        path('', prospect.list_prospects, name='prospects'),
        path('<int:prospect_id>/', prospect.prospect_details, name='prospect_details'),
        path('reporting', prospect.prospect_xls, name='prospects_xls'),
        path('delete', prospect.delete_prospects, name='prospects_delete'),
    ])),
    path('tasks/', include([
        path('', tasks.list_tasks, name='list_tasks'),
        path('paper_registrations_file_received', tasks.paper_registrations_file_received,
             name='paper_registrations_file_received'),
        path('mark_diplomas_produced', tasks.mark_diplomas_produced, name='mark_diplomas_produced'),
        path('process_admissions', tasks.process_admissions, name='process_admissions'),
    ])),
    path('training-autocomplete/', ContinuingEducationTrainingAutocomplete.as_view(), name='training_autocomplete'),
    path('managers/', include([
        path('', managers.list_managers, name='list_managers'),
        path('add/', managers.add_continuing_education_training_manager,
             name='add_continuing_education_training_manager'),
        path('delete/<int:training>/<int:manager>', managers.delete_continuing_education_training_manager,
             name='delete_continuing_education_training_manager')
    ])),
    path('injection/<int:admission_id>/', registration_queue.inject_admission_to_epc, name='injection_to_epc')
]
