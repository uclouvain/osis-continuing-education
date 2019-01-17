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
from rest_framework import generics

from continuing_education.api.serializers.address import AddressSerializer
from continuing_education.models.address import Address


class AddressListCreate(generics.ListCreateAPIView):
    """
       Return a list of all the addresses with optional filtering or create an addreess.
    """
    name = 'address-list-create'
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    filter_fields = (
        'country',
        'city',
    )
    search_fields = (
        'location',
        'city',
    )


class AddressDetail(generics.RetrieveAPIView):
    """
        Return the detail of the address
    """
    name = 'address-detail'
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    lookup_field = 'uuid'
