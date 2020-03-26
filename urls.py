##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf.urls import url, include

import continuing_education.views.file
from continuing_education.business import registration_queue
from continuing_education.views import (home, admission, registration, archive, formation, prospect, tasks, managers)
from continuing_education.views.autocomplete.continuing_education_training import \
    ContinuingEducationTrainingAutocomplete

urlpatterns = [
    url(r'^$', home.main_view, name='continuing_education'),
    url(r'^admission/', include([
        url(r'^$', admission.list_admissions, name='admission'),
        url(r'^new/$', admission.admission_form, name='admission_new'),
        url(r'^edit/(?P<admission_id>[0-9]+)/', admission.admission_form, name='admission_edit'),
        url(r'^(?P<admission_id>[0-9]+)/', include([
            url(r'^$', admission.admission_detail, name='admission_detail'),
            url(r'^send_invoice_notification_mail/$', admission.send_invoice_notification_mail,
                name='send_invoice_notification_mail'),
            url(r'^file/(?P<file_id>[0-9]+)$', continuing_education.views.file.download_file, name='download_file'),
            url(r'file/(?P<file_id>[0-9]+)/delete$', continuing_education.views.file.delete_file, name='delete_file'),
        ])),
        url(r'^validate_field/(?P<admission_id>[0-9]+)/$', admission.validate_field, name='validate_field'),
        url(r'^ajax/formation/', admission.get_formation_information, name='get_formation_information'),
        url(r'^billing_edit/(?P<admission_id>[0-9]+)/', admission.billing_edit, name='billing_edit'),
    ])),
    url(r'^registration/', include([
        url(r'^$', registration.list_registrations, name='registration'),
        url(r'^edit/(?P<admission_id>[0-9]+)/', registration.registration_edit, name='registration_edit'),
        url(r'^list/receive_files/', registration.receive_files_procedure, name='receive_files_procedure'),
        url(r'^change_received_file_state/(?P<admission_id>[0-9]+)/', registration.receive_file_procedure,
            name='receive_file_procedure'),
        url(r'^cancelled/', registration.list_cancelled, name='cancelled_files'),
    ])),
    url(r'^archive/', include([
        url(r'^$', archive.list_archives, name='archive'),
        url(r'^list/to_archive/', archive.archives_procedure, name='archives_procedure'),
        url(r'^list/to_unarchive/', archive.unarchives_procedure, name='unarchives_procedure'),
        url(r'^to_archive/(?P<admission_id>[0-9]+)/', archive.archive_procedure, name='archive_procedure'),
    ])),
    url(r'^formation/', include([
        url(r'^$', formation.list_formations, name='formation'),
        url(r'^list/update/', formation.update_formations, name='update_formations'),
        url(r'^(?P<formation_id>[0-9]+)/', formation.formation_detail, name='formation_detail'),
        url(r'^edit/(?P<formation_id>[0-9]+)/', formation.formation_edit, name='formation_edit'),
    ])),
    url(r'^prospects/', include([
        url(r'^$', prospect.list_prospects, name='prospects'),
        url(r'^(?P<prospect_id>[0-9]+)/', prospect.prospect_details, name='prospect_details'),
        url(r'^reporting', prospect.prospect_xls, name='prospects_xls'),
    ])),
    url(r'^tasks/', include([
        url(r'^$', tasks.list_tasks, name='list_tasks'),
        url(r'^paper_registrations_file_received', tasks.paper_registrations_file_received,
            name='paper_registrations_file_received'),
        url(r'^mark_diplomas_produced', tasks.mark_diplomas_produced, name='mark_diplomas_produced'),
        url(r'^process_admissions', tasks.process_admissions, name='process_admissions'),
    ])),
    url(r'^training-autocomplete/$', ContinuingEducationTrainingAutocomplete.as_view(), name='training_autocomplete'),
    url(r'^managers/', include([
        url(r'^$', managers.list_managers, name='list_managers'),
        url(r'^add/', managers.add_person_training, name='add_person_training'),
        url(r'^delete/(?P<training>[0-9]+)/(?P<manager>[0-9]+)',
            managers.delete_person_training, name='delete_person_training')
    ])),
    url(r'^injection/(?P<admission_id>[0-9]+)/', registration_queue.inject_admission_to_epc, name='injection_to_epc')
]
