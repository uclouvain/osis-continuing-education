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
from django.core import serializers
from django.http import HttpResponse
from rest_framework import views, status
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response

from continuing_education.models.admission import Admission
from continuing_education.models.file import File


class FileAPIView(views.APIView):
    parser_classes = (MultiPartParser,)

    def get(self, request):
        if 'file_path' in request.query_params:
            file_path = request.query_params['file_path']
            return _send_file(file_path)
        elif 'admission_id' in request.query_params:
            admission_id = request.query_params['admission_id']
            return _send_documents_list(admission_id)
        else:
            return Response(
                data="File not found",
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request):
        admission_id = request.data['admission_id']
        file_obj = request.data['file']
        admission = Admission.objects.get(pk=admission_id)
        file = File(admission=admission, name=file_obj.name ,path=file_obj)
        file.save()
        return Response(
            data="File uploaded sucessfully",
            status=status.HTTP_201_CREATED
        )

def _send_file(file_path):
    file = File.objects.get(path=file_path)
    response = HttpResponse(file.path, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % file.name
    return response

def _send_documents_list(admission_id):
    admission = Admission.objects.get(pk=admission_id)
    documents = File.objects.filter(admission=admission)
    documents_json = serializers.serialize("json", documents)
    return HttpResponse(documents_json)
