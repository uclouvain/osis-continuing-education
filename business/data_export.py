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
from uuid import UUID

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from continuing_education.business.serializers.export_json import ExportJsonSerializer

APPLICATION_JSON_CONTENT_TYPE = 'application/json'


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


def create_json(request, registrations):
    serializer = ExportJsonSerializer(
        registrations,
        many=True,
        context={'request': request})

    filename = "%s_export.json" % (_('Registrations'))

    response = HttpResponse(
        json.dumps(serializer.data, cls=UUIDEncoder),
        content_type=APPLICATION_JSON_CONTENT_TYPE)
    response['Content-Disposition'] = "%s%s" % ("attachment; filename=", filename)

    return response
