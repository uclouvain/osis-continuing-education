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
import base64

from rest_framework import serializers
from rest_framework.reverse import reverse

from base.api.serializers.person import PersonDetailSerializer
from base.models.person import Person
from continuing_education.models.enums import file_category_choices
from continuing_education.models.file import AdmissionFile


class AdmissionFileHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):
    def __init__(self, **kwargs):
        super().__init__(view_name='continuing_education_api_v1:file-detail-delete', **kwargs)

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            'uuid': obj.admission.uuid,
            'file_uuid': obj.uuid
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)


class AdmissionFileSerializer(serializers.HyperlinkedModelSerializer):
    url = AdmissionFileHyperlinkedIdentityField()
    created_date = serializers.DateTimeField(read_only=True)
    uploaded_by = PersonDetailSerializer(read_only=True)
    content = serializers.SerializerMethodField()
    file_category_text = serializers.CharField(source='get_file_category_display', read_only=True)

    def get_content(self, file):
        file.content = base64.b64encode(file.path.read())
        return file.content

    class Meta:
        model = AdmissionFile
        fields = (
            'url',
            'uuid',
            'name',
            'path',
            'size',
            'created_date',
            'uploaded_by',
            'content',
            'file_category',
            'file_category_text'
        )


class AdmissionFilePostSerializer(AdmissionFileSerializer):
    created_date = serializers.DateTimeField(required=False, read_only=True)
    uploaded_by = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Person.objects.all()
    )
    name = serializers.CharField(required=False)

    def create(self, validated_data):
        validated_data['admission'] = self.context['admission']
        validated_data['file_category'] = file_category_choices.PARTICIPANT
        return super().create(validated_data)
