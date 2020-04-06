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
import random

import factory

from base.tests.factories.academic_year import AcademicYearFactory
from continuing_education.models.enums import admission_state_choices, enums
from continuing_education.models.enums.ucl_registration_error_choices import UCLRegistrationError
from continuing_education.models.enums.ucl_registration_state_choices import UCLRegistrationState
from continuing_education.tests.factories.address import AddressFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory
from continuing_education.tests.utils.utils import get_enum_keys
from reference.tests.factories.country import CountryFactory

CONTINUING_EDUCATION_TYPE = 8


def _get_fake_phone_number():
    factory.Faker._DEFAULT_LOCALE = 'nl_BE'
    fake = factory.Faker('phone_number').generate(extra_kwargs={})
    for c in [" ", "(", ")", "-"]:
        fake = fake.replace(c, "")
    factory.Faker._DEFAULT_LOCALE = 'en_US'
    return fake


class AdmissionFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'continuing_education.admission'

    person_information = factory.SubFactory(ContinuingEducationPersonFactory)

    # Identification
    citizenship = factory.SubFactory(CountryFactory)

    # Contact
    phone_mobile = _get_fake_phone_number()
    email = factory.Faker('email')

    address = factory.SubFactory(AddressFactory)

    # Education
    high_school_diploma = factory.fuzzy.FuzzyChoice([True, False])
    high_school_graduation_year = factory.fuzzy.FuzzyInteger(1991, 2018)
    last_degree_level = "level"
    last_degree_field = "field"
    last_degree_institution = "institution"
    last_degree_graduation_year = factory.fuzzy.FuzzyInteger(1991, 2018)
    other_educational_background = "other background"

    # Professional Background
    professional_status = factory.fuzzy.FuzzyChoice(get_enum_keys(enums.STATUS_CHOICES))

    current_occupation = factory.Faker('text', max_nb_chars=50)
    current_employer = factory.Faker('company')

    activity_sector = factory.fuzzy.FuzzyChoice(get_enum_keys(enums.SECTOR_CHOICES))

    past_professional_activities = "past activities"

    # Motivation
    motivation = "motivation"
    professional_personal_interests = "professional impact"

    # Formation
    formation = factory.SubFactory(ContinuingEducationTrainingFactory)
    academic_year = factory.SubFactory(AcademicYearFactory)

    # Awareness
    awareness_ucl_website = factory.fuzzy.FuzzyChoice([True, False])
    awareness_formation_website = factory.fuzzy.FuzzyChoice([True, False])
    awareness_press = factory.fuzzy.FuzzyChoice([True, False])
    awareness_facebook = factory.fuzzy.FuzzyChoice([True, False])
    awareness_linkedin = factory.fuzzy.FuzzyChoice([True, False])
    awareness_customized_mail = factory.fuzzy.FuzzyChoice([True, False])
    awareness_emailing = factory.fuzzy.FuzzyChoice([True, False])
    awareness_other = factory.Sequence(lambda n: 'Other %d' % n)
    awareness_word_of_mouth = factory.fuzzy.FuzzyChoice([True, False])
    awareness_friends = factory.fuzzy.FuzzyChoice([True, False])
    awareness_former_students = factory.fuzzy.FuzzyChoice([True, False])
    awareness_moocs = factory.fuzzy.FuzzyChoice([True, False])

    # State
    state = factory.fuzzy.FuzzyChoice(get_enum_keys(admission_state_choices.STATE_CHOICES))

    # Billing
    registration_type = factory.fuzzy.FuzzyChoice(get_enum_keys(enums.REGISTRATION_TITLE_CHOICES))

    use_address_for_billing = factory.fuzzy.FuzzyChoice([True, False])
    billing_address = factory.SubFactory(AddressFactory)

    head_office_name = factory.Faker('company')
    company_number = factory.Faker('isbn10')
    vat_number = factory.Faker('ssn')

    # Registration
    national_registry_number = factory.Faker('ssn')
    id_card_number = factory.Faker('ssn')
    passport_number = factory.Faker('isbn13')

    marital_status = factory.fuzzy.FuzzyChoice(get_enum_keys(enums.MARITAL_STATUS_CHOICES))

    spouse_name = factory.Faker('name')
    children_number = random.randint(0, 10)
    previous_ucl_registration = factory.fuzzy.FuzzyChoice([True, False])
    previous_noma = factory.Faker('isbn10')

    # Post
    use_address_for_post = factory.fuzzy.FuzzyChoice([True, False])
    residence_address = factory.SubFactory(AddressFactory)
    residence_phone = _get_fake_phone_number(),

    # Student Sheet
    ucl_registration_complete = UCLRegistrationState.INIT_STATE.name
    ucl_registration_error = UCLRegistrationError.IUFC_NO_ERROR.name

    noma = factory.Faker('isbn10')
    payment_complete = factory.fuzzy.FuzzyChoice([True, False])
    formation_spreading = factory.fuzzy.FuzzyChoice([True, False])
    prior_experience_validation = factory.fuzzy.FuzzyChoice([True, False])
    assessment_presented = factory.fuzzy.FuzzyChoice([True, False])
    assessment_succeeded = factory.fuzzy.FuzzyChoice([True, False])
    registration_file_received = False
    archived = False
    diploma_produced = False

    # TODO:: For sessions, add dates of followed courses (see model)
    sessions = "sessions"
    reduced_rates = False
    spreading_payments = False
    condition_of_acceptance = ''
    comment = ''
