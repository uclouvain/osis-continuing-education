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
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from continuing_education.api.serializers.file import AdmissionFileSerializer, AdmissionFilePostSerializer
from continuing_education.api.views.perms.perms import CanSendFiles
from continuing_education.models.admission import Admission
from continuing_education.models.enums.exceptions import APIFileUploadExceptions
from continuing_education.models.file import AdmissionFile


class AdmissionFileListCreate(generics.ListCreateAPIView):
    """
       Return a list of all the files with optional filtering.
    """
    name = 'file-list-create'
    filter_fields = (
        'name',
        'size',
        'created_date',
        'uploaded_by'
    )
    search_fields = (
        'name',
        'path',
        'size',
        'created_date',
        'uploaded_by'
    )
    permission_classes = (CanSendFiles, IsAuthenticated)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except APIFileUploadExceptions as e:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=str(e)
            )
        except ValidationError as e:
            return Response(
                status=status.HTTP_406_NOT_ACCEPTABLE,
                data=next(iter(e.detail.values()))
            )
        except Exception as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=_("A problem occured : the document is not uploaded")
            )

    def get_queryset(self):
        admission = get_object_or_404(Admission, uuid=self.kwargs['uuid'])
        return AdmissionFile.objects.filter(admission=admission)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AdmissionFilePostSerializer
        return AdmissionFileSerializer

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        if self.request.method == 'POST':
            serializer_context['admission'] = get_object_or_404(Admission, uuid=self.kwargs['uuid'])
        return serializer_context


class AdmissionFileRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """
        Return the detail of the file or destroy it
    """
    name = 'file-detail-delete'
    queryset = AdmissionFile.objects.all()
    serializer_class = AdmissionFileSerializer
    lookup_field = 'uuid'
    permission_classes = (CanSendFiles, IsAuthenticated)

    def get_object(self):
        admission_file = get_object_or_404(AdmissionFile, uuid=self.kwargs['file_uuid'])
        return admission_file
