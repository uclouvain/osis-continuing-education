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

from django.test import TestCase
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse

from base.tests.factories.person import PersonFactory
from continuing_education.models.enums import admission_state_choices
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from continuing_education.business.data_export import create_json, APPLICATION_JSON_CONTENT_TYPE


class DataExportTestCase(TestCase):

    def setUp(self):
        a_person = PersonFactory(last_name="Martin")
        a_continuing_education_person = ContinuingEducationPersonFactory(person=a_person)
        self.registration = AdmissionFactory(state=admission_state_choices.VALIDATED,
                                             person_information=a_continuing_education_person)
        self.registrations = [self.registration]

    def test_data_export_response(self):
        response = create_json(self.registrations)

        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], APPLICATION_JSON_CONTENT_TYPE)
        self.assertEqual(response['Content-Disposition'], "%s%s" % ("attachment; filename=",
                                                                    "%s_export.json" % (_('Registrations'))))

    def test_data_export_content(self):
        response = create_json(self.registrations)
        json_response = str(response.content, encoding='utf8')
        data = json.loads(json_response)

        registration_data = data[0]
        self.assertEqual(registration_data['id'], self.registration.id)

        person_information_data = registration_data['person_information']
        self.assertEqual(person_information_data['id'], self.registration.person_information.id)
        self.assertEqual(person_information_data['person']['last_name'],
                         self.registration.person_information.person.last_name)

        self.assertEqual(registration_data['formation']['id'], self.registration.formation.id)

        address_data = registration_data['address']
        self.assertEqual(address_data['id'], self.registration.address.id)
        self.assertEqual(address_data['country']['id'], self.registration.address.country.id)



