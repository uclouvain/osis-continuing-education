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
import datetime
import random

import factory

import reference
from base.models import entity_version
from base.models.academic_year import current_academic_years
from base.models.enums import entity_type
from base.models.offer_year import OfferYear
from continuing_education.models.enums.enums import STATE_CHOICES, REGISTRATION_TITLE_CHOICES, MARITAL_STATUS_CHOICES
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from continuing_education.tests.utils.utils import get_enum_keys

CONTINUING_EDUCATION_TYPE = 8

class AdmissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'continuing_education.admission'

    @staticmethod
    def populate(country_id):
        country = reference.models.country.find_by_id(country_id)
        formation = OfferYear.objects.filter(offer_type_id=CONTINUING_EDUCATION_TYPE, academic_year_id=current_academic_years()).order_by('?').first()
        faculty = entity_version.find_latest_version(datetime.datetime.now()).filter(entity_type=entity_type.FACULTY).order_by('?').first()
        AdmissionFactory.create(
            birth_country = country,
            country = country,
            citizenship = country,
            billing_country = country,
            residence_country = country,
            formation = formation,
            faculty = faculty
        )

    person_information = factory.SubFactory(ContinuingEducationPersonFactory)

    # Motivation
    motivation = "motivation"
    professional_impact = "professional impact"

    # Formation
    formation = "EXAMPLE"

    # Awareness
    awareness_ucl_website = factory.fuzzy.FuzzyChoice([True, False])
    awareness_formation_website = factory.fuzzy.FuzzyChoice([True, False])
    awareness_press = factory.fuzzy.FuzzyChoice([True, False])
    awareness_facebook = factory.fuzzy.FuzzyChoice([True, False])
    awareness_linkedin = factory.fuzzy.FuzzyChoice([True, False])
    awareness_customized_mail = factory.fuzzy.FuzzyChoice([True, False])
    awareness_emailing = factory.fuzzy.FuzzyChoice([True, False])

    # State
    state = factory.fuzzy.FuzzyChoice(get_enum_keys(STATE_CHOICES))

    # Billing
    registration_type = factory.fuzzy.FuzzyChoice(get_enum_keys(REGISTRATION_TITLE_CHOICES))

    use_address_for_billing = factory.fuzzy.FuzzyChoice([True, False])
    billing_address = factory.SubFactory(AddressFactory)

    head_office_name = factory.Faker('company')
    company_number = factory.Faker('isbn10')
    vat_number = factory.Faker('ssn')

    # Registration
    national_registry_number = factory.Faker('ssn')
    id_card_number = factory.Faker('ssn')
    passport_number = factory.Faker('isbn13')

    marital_status = factory.fuzzy.FuzzyChoice(get_enum_keys(MARITAL_STATUS_CHOICES))

    spouse_name = factory.Faker('name')
    children_number = random.randint(0,10)
    previous_ucl_registration = factory.fuzzy.FuzzyChoice([True, False])
    previous_noma = factory.Faker('isbn10')

    # Post
    use_address_for_post = factory.fuzzy.FuzzyChoice([True, False])
    residence_address = factory.SubFactory(AddressFactory)
    residence_phone = factory.Faker('phone_number')

    # Student Sheet
    registration_complete = factory.fuzzy.FuzzyChoice([True, False])
    noma = factory.Faker('isbn10')
    payment_complete = factory.fuzzy.FuzzyChoice([True, False])
    formation_spreading = factory.fuzzy.FuzzyChoice([True, False])
    prior_experience_validation = factory.fuzzy.FuzzyChoice([True, False])
    assessment_presented = factory.fuzzy.FuzzyChoice([True, False])
    assessment_succeeded = factory.fuzzy.FuzzyChoice([True, False])
    # ajouter dates sessions cours suivies
    sessions = "sessions"
