##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import serializers
from rest_framework.reverse import reverse

from base.api.serializers.person import PersonDetailSerializer
from continuing_education.models.file import File


class FileHyperlink(serializers.HyperlinkedRelatedField):
    view_name = 'continuing_education_api_v1:file-detail'
    queryset = File.objects.all()

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'uuid': obj.admission.uuid,
            'file_uuid': obj.uuid
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
           'uuid': view_kwargs['file_uuid'],
           'admission__uuid': view_kwargs['uuid']
        }
        return self.get_queryset().get(**lookup_kwargs)


class FileSerializer(serializers.ModelSerializer):
    url = FileHyperlink
    uploaded_by = PersonDetailSerializer()
    created_date = serializers.DateTimeField()

    class Meta:
        model = File
        fields = (
            'uuid',
            'url',
            'name',
            'path',
            'size',
            'created_date',
            'uploaded_by'
        )
