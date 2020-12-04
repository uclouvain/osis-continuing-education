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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

from django.test import TestCase

from base.tests.factories.academic_year import create_current_academic_year
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from continuing_education.business.xls.xls_common import extract_xls_data_from_admission, \
    extract_xls_data_from_registration
from continuing_education.models.enums.admission_state_choices import ACCEPTED
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from reference.tests.factories.country import CountryFactory

IDX_COL_MAIL = 2
IDX_COL_BIRTHDATE = 6

CITY_NAME = 'Moignelée'
COUNTRY_NAME = 'Algérie'


class TestXlsCommon(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=create_current_academic_year()
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )
        algeria = CountryFactory(name=COUNTRY_NAME)
        cls.address = AddressFactory(city=CITY_NAME,
                                     country=algeria,
                                     location='Street',
                                     postal_code='5500')

        cls.registration = AdmissionFactory(
            formation=cls.formation,
            state=ACCEPTED,
            ucl_registration_complete=True,
            payment_complete=False,
            citizenship=algeria,
            person_information=ContinuingEducationPersonFactory(birth_location=CITY_NAME,
                                                                birth_country=algeria,
                                                                birth_date=datetime.datetime(1977, 4, 22)),
            address=cls.address,
            billing_address=cls.address,
            residence_address=cls.address
        )

    def test_upper_in_country_city(self):
        result = extract_xls_data_from_admission(self.registration)
        self.assertEqual(result[5], COUNTRY_NAME.upper())
        self.assertEqual(result[7], CITY_NAME.upper())
        self.assertEqual(result[8], COUNTRY_NAME.upper())

        result = extract_xls_data_from_registration(self.registration)
        self.assertEqual(result[10], "{} - {} {} - {}".format(self.address.location, self.address.postal_code,
                                                              self.address.city.upper(), COUNTRY_NAME.upper()))
        self.assertEqual(result[35], "{} - {} {} - {}".format(self.address.location, self.address.postal_code,
                                                              self.address.city.upper(), COUNTRY_NAME.upper()))
        self.assertEqual(result[10], "{} - {} {} - {}".format(self.address.location, self.address.postal_code,
                                                              self.address.city.upper(), COUNTRY_NAME.upper()))

    def test_birth_date(self):
        result = extract_xls_data_from_admission(self.registration)
        self.assertEqual(result[IDX_COL_BIRTHDATE], self.registration.person_information.birth_date)

        result = extract_xls_data_from_registration(self.registration)
        self.assertEqual(result[IDX_COL_BIRTHDATE], self.registration.person_information.birth_date)

    def test_email(self):
        result = extract_xls_data_from_admission(self.registration)
        self.assertEqual(result[IDX_COL_MAIL], self.registration.person_information.person.email)

        result = extract_xls_data_from_registration(self.registration)
        self.assertEqual(result[IDX_COL_MAIL], self.registration.person_information.person.email)
