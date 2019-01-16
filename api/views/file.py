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
from rest_framework import generics
from rest_framework.generics import DestroyAPIView, CreateAPIView

from continuing_education.api.serializers.file import FileSerializer, FilePostSerializer
from continuing_education.models.admission import Admission
from continuing_education.models.file import File


class FileList(generics.ListAPIView):
    """
       Return a list of all the files with optional filtering.
    """
    name = 'file-list'
    serializer_class = FileSerializer
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
        return File.objects.filter(admission=admission)


class FileDetail(generics.RetrieveAPIView):
    """
        Return the detail of the file
    """
    name = 'file-detail'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = 'uuid'

    def get_object(self):
        file = get_object_or_404(File, uuid=self.kwargs['file_uuid'])
        return file


class FileDestroy(DestroyAPIView):
    """
        Remove a file
    """
    name = 'file-delete'
    queryset = File.objects.all()
    serializer_class = FileSerializer
    lookup_field = 'uuid'

    def get_object(self):
        file = get_object_or_404(File, uuid=self.kwargs['file_uuid'])
        return file


class FileCreate(CreateAPIView):

    """
        Create a file
    """
    name = 'file-create'
    serializer_class = FilePostSerializer

    def get_serializer_context(self):
        serializer_context = super().get_serializer_context()
        serializer_context['admission'] = Admission.objects.get(uuid=self.kwargs['uuid'])
        return serializer_context
