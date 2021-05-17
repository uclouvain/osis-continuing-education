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

from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from reference.tests.factories.country import CountryFactory


class ContinuingEducationPersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'continuing_education.ContinuingEducationPerson'

    person = factory.SubFactory(PersonFactory)

    # Identification
    birth_location = factory.Faker('city')
    birth_country = factory.SubFactory(CountryFactory)
    birth_date = factory.fuzzy.FuzzyDate(datetime.datetime(1977, 1, 1),
                                         datetime.datetime(2001, 3, 1))
