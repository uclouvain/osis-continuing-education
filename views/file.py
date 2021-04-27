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
import mimetypes

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import permission_required

from base.models.person import Person
from base.views.common import display_success_messages, display_error_messages
from continuing_education.business.admission import send_invoice_uploaded_email
from continuing_education.models.admission import admission_getter
from continuing_education.models.enums import admission_state_choices, file_category_choices
from continuing_education.models.enums.exceptions import ManagerFileUploadExceptions
from continuing_education.models.file import AdmissionFile
from osis_common.decorators.download import set_download_cookie


def _get_file_category_choices_with_disabled_parameter(admission):
    invoice_choice_disabled = admission.state != admission_state_choices.ACCEPTED
    return (
        choice + ("disabled",)
        if choice[0] == file_category_choices.INVOICE and invoice_choice_disabled
        else choice + ("",)
        for choice in file_category_choices.FILE_CATEGORY_CHOICES
    )


def _upload_file(request, admission):
    my_file = request.FILES['myfile']
    file_category = request.POST.get('file_category', None)
    person = Person.objects.get(user=request.user)

    file_to_admission = AdmissionFile(
        admission=admission,
        path=my_file,
        name=my_file.name,
        size=my_file.size,
        uploaded_by=person,
        file_category=file_category,
    )

    try:
        file_to_admission.save()
        display_success_messages(request, _("The document is uploaded correctly"))
        if _email_notification_must_be_sent(file_category, request):
            send_invoice_uploaded_email(admission)
            display_success_messages(request, _("A notification email has been sent to the participant"))

    except ManagerFileUploadExceptions as e:
        display_error_messages(request, str(e))
    except Exception as e:
        display_error_messages(request, _("A problem occured : the document is not uploaded"))

    return redirect(reverse('admission_detail', kwargs={'admission_id': admission.pk}) + '#documents')


@login_required
@permission_required('continuing_education.view_admission', fn=admission_getter, raise_exception=True)
@set_download_cookie
def download_file(request, admission_id, file_id):
    file = AdmissionFile.objects.get(pk=file_id)
    filename = file.name.split('/')[-1]
    response = HttpResponse(file.path, content_type=mimetypes.guess_type(filename))
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


@login_required
@permission_required('continuing_education.change_admission', fn=admission_getter, raise_exception=True)
def delete_file(request, admission_id, file_id):
    file = AdmissionFile.objects.filter(id=file_id)
    try:
        file.delete()
        display_success_messages(request, _("File correctly deleted"))
    except Exception as e:
        display_error_messages(request, _("A problem occured during delete"))
    return redirect(reverse('admission_detail', kwargs={'admission_id': admission_id}) + '#documents')


def _email_notification_must_be_sent(file_category, request):
    return file_category == file_category_choices.INVOICE and request.POST.get('notify_participant', None)
