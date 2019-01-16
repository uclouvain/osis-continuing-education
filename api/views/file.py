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

from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from continuing_education.api.serializers.file import AdmissionFileSerializer, AdmissionFilePostSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.file import AdmissionFile


class AdmissionFileList(generics.ListAPIView):
    """
       Return a list of all the files with optional filtering.
    """
    name = 'file-list'
    serializer_class = AdmissionFileSerializer
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

    def get_queryset(self):
        admission = get_object_or_404(Admission, uuid=self.kwargs['uuid'])
        return AdmissionFile.objects.filter(admission=admission)


class AdmissionFileCreate(CreateAPIView):

    """
        Create a file
    """
    name = 'file-create'
    serializer_class = AdmissionFilePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=False)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
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

    def get_object(self):
        admission_file = get_object_or_404(AdmissionFile, uuid=self.kwargs['file_uuid'])
        return admission_file
