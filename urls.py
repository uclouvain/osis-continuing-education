##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from continuing_education.views import (home, admission, registration, archive, formation, prospect, tasks)

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
        ]))
    ])),
    url(r'^registration/', include([
        url(r'^$', registration.list_registrations, name='registration'),
        url(r'^edit/(?P<admission_id>[0-9]+)/', registration.registration_edit, name='registration_edit'),
    ])),
    url(r'^archive/', include([
        url(r'^$', archive.list_archives, name='archive'),
        url(r'^list/to_archive/', archive.archives_procedure, name='archives_procedure'),
        url(r'^to_archive/(?P<admission_id>[0-9]+)/', archive.archive_procedure, name='archive_procedure'),
    ])),
    url(r'^formation/', include([
        url(r'^$', formation.list_formations, name='formation'),
    ])),
    url(r'^prospects$', prospect.list_prospects, name='prospects'),
    url(r'^tasks/', include([
        url(r'^$', tasks.list_tasks, name='list_tasks'),
        url(r'^validate_registrations', tasks.validate_registrations, name='validate_registrations'),
    ])),
]
