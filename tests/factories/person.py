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
import factory

from continuing_education.models.person import Person
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.utils.utils import _get_random_choices
from reference.tests.factories.country import CountryFactory


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'continuing_education.person'

   # Identification
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    birth_date = factory.LazyFunction(datetime.datetime.now)
    birth_location = factory.Faker('city')
    birth_country = factory.SubFactory(CountryFactory)
    citizenship = factory.SubFactory(CountryFactory)

    gender = factory.fuzzy.FuzzyChoice(_get_random_choices(Person.GENDER_CHOICES))

    # Contact
    phone_mobile = factory.Faker('phone_number')
    email = factory.Faker('email')

    address = factory.SubFactory(AddressFactory)

    # Education
    high_school_diploma = factory.fuzzy.FuzzyChoice([True, False])
    high_school_graduation_year = factory.LazyFunction(datetime.datetime.now)
    last_degree_level = "level"
    last_degree_field = "field"
    last_degree_institution = "institution"
    last_degree_graduation_year = factory.LazyFunction(datetime.datetime.now)
    other_educational_background = "other background"

    # Professional Background
    professional_status = factory.fuzzy.FuzzyChoice(_get_random_choices(Person.STATUS_CHOICES))

    current_occupation = factory.Faker('text', max_nb_chars=50)
    current_employer = factory.Faker('company')

    activity_sector = factory.fuzzy.FuzzyChoice(_get_random_choices(Person.SECTOR_CHOICES))

    past_professional_activities = "past activities"