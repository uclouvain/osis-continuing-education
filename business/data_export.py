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
import json

from django.http import HttpResponse
from rest_framework import serializers

from continuing_education.models.admission import Admission
from continuing_education.models.continuing_education_person import ContinuingEducationPerson
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.address import Address
from continuing_education.api.serializers.address import AddressSerializer
from reference.models.country import Country


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = Address
        fields = '__all__'


class ContinuingEducationPersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContinuingEducationPerson
        fields = '__all__'


class ContinuingEducationTrainingSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContinuingEducationTraining
        fields = '__all__'


class AdmissionSerializer(serializers.ModelSerializer):

    person_information = ContinuingEducationPersonSerializer(read_only=True)
    formation = ContinuingEducationTrainingSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    residence_address = AddressSerializer(read_only=True)

    class Meta:
        model = Admission
        fields = '__all__'


def create_json(registrations):
    serializer = AdmissionSerializer(registrations, many=True)
    filename = "%s_export.json" % (_('Registrations'))
    response = HttpResponse(
        json.dumps(serializer.data),
        content_type='application/json')
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)

    return response
