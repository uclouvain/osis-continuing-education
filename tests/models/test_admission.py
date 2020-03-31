##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from unittest.mock import patch

from django.test import TestCase
from django.utils.translation import gettext as _

from base.models.enums.entity_type import SCHOOL
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.business.entities import create_entities_hierarchy
from base.tests.factories.education_group import EducationGroupFactory
from base.tests.factories.education_group_year import EducationGroupYearFactory
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from continuing_education.models import admission
from continuing_education.models.admission import Admission
from continuing_education.models.enums import admission_state_choices
from continuing_education.tests.factories.admission import AdmissionFactory
from continuing_education.tests.factories.continuing_education_training import ContinuingEducationTrainingFactory
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory as PersonFactory
from continuing_education.tests.factories.person import ContinuingEducationPersonFactory


class TestAdmission(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group
        )

    def test_search(self):
        an_admission = AdmissionFactory(formation=self.formation)
        persisted_admission = admission.search(person=an_admission.person_information)
        self.assertTrue(persisted_admission.exists())

        nonexistent_admission = admission.search(person=ContinuingEducationPersonFactory())
        self.assertFalse(nonexistent_admission.exists())

    @patch('osis_common.messaging.send_message.send_messages')
    def test_mail_not_sent_on_same_admission_state(self, mock):
        AdmissionFactory(state=admission_state_choices.SUBMITTED, formation=self.formation).save()
        self.assertFalse(mock.called)

    def test_admission_ordering(self):
        ed = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed,
            academic_year=self.academic_year,
            acronym='M'
        )
        cet = ContinuingEducationTrainingFactory(education_group=ed)
        ed_next = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=ed_next,
            academic_year=self.academic_year,
            acronym='O'
        )
        cet_next = ContinuingEducationTrainingFactory(education_group=ed_next)
        persons_data = [
            ('A', 'I', cet),
            ('D', 'J', cet),
            ('C', 'J', cet),
            ('B', 'I', cet),
            ('E', 'K', cet_next),
            ('H', 'L', cet_next),
            ('G', 'L', cet_next),
            ('F', 'K', cet_next)
        ]
        for first_name, name, formation in persons_data:
            a_person = ContinuingEducationPersonFactory(person=PersonFactory(first_name=first_name, last_name=name))
            AdmissionFactory(person_information=a_person, formation=formation)
        expected_order = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        result = Admission.objects.all().values_list(
            'person_information__person__first_name', flat=True
        )
        self.assertEquals(list(result), expected_order)


class TestAdmissionGetProperties(TestCase):
    @classmethod
    def setUpTestData(cls):
        entities = create_entities_hierarchy()
        cls.faculty = entities['child_one_entity_version']
        cls.child_entity = EntityFactory(country=entities['country'], organization=entities['organization'])
        cls.child_entity_version = EntityVersionFactory(acronym="CHILD_1_UNDER_FAC",
                                                        parent=cls.faculty.entity,
                                                        entity_type=SCHOOL,
                                                        end_date=None,
                                                        entity=cls.child_entity,
                                                        start_date=entities['start_date'])
        cls.academic_year = AcademicYearFactory(year=2018)
        cls.education_group = EducationGroupFactory()
        EducationGroupYearFactory(
            education_group=cls.education_group,
            academic_year=cls.academic_year,
            management_entity=cls.child_entity
        )
        cls.formation = ContinuingEducationTrainingFactory(
            education_group=cls.education_group,
        )
        cls.admission = AdmissionFactory(formation=cls.formation,
                                         awareness_ucl_website=False,
                                         awareness_formation_website=False,
                                         awareness_press=False,
                                         awareness_facebook=True,
                                         awareness_linkedin=False,
                                         awareness_customized_mail=False,
                                         awareness_emailing=False,
                                         awareness_other='Other awareness',
                                         awareness_word_of_mouth=False,
                                         awareness_friends=False,
                                         awareness_former_students=False,
                                         awareness_moocs=False)

    def test_get_faculty(self):
        an_admission = AdmissionFactory(
            formation=self.formation
        )
        self.assertEqual(an_admission.get_faculty(), self.child_entity)

    def test_awareness_list(self):
        self.assertEqual(self.admission.awareness_list, "{}, {} : {}".format(_("By Facebook"),
                                                                             _('Other'),
                                                                             'Other awareness'))
        self.admission.awareness_other = ''
        self.admission.save()
        self.assertEqual(self.admission.awareness_list, "{}".format(_("By Facebook")))
