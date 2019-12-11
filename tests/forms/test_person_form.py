from django.forms import model_to_dict
from django.test import TestCase

from base.tests.factories.person import PersonFactory
from continuing_education.forms.person import PersonForm


class TestPersonForm(TestCase):

    def test_valid_form(self):
        person = PersonFactory()
        form = PersonForm(data=model_to_dict(person), selected_person=False, no_first_name_checked=False)
        self.assertTrue(form.is_valid(), form.errors)

    def test_selected_person_form(self):
        person = PersonFactory()
        form = PersonForm(data=model_to_dict(person), selected_person=True, no_first_name_checked=False)
        self.assertTrue(form.is_valid(), form.errors)

    def test_no_first_name_form(self):
        person = PersonFactory(first_name='')
        form = PersonForm(data=model_to_dict(person), selected_person=False, no_first_name_checked=True)
        self.assertTrue(form.is_valid(), form.errors)
