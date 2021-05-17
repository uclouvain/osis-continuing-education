from django.forms import model_to_dict
from django.test import TestCase

from continuing_education.forms.person import PersonForm
from continuing_education.tests.factories.iufc_person import IUFCPersonFactory


class TestPersonForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = model_to_dict(IUFCPersonFactory())

    def test_valid_form(self):
        form = PersonForm(data=self.data, selected_person=False, no_first_name_checked=False)
        self.assertTrue(form.is_valid(), form.errors)

    def test_selected_person_form(self):
        form = PersonForm(data=self.data, selected_person=True, no_first_name_checked=False)
        self.assertTrue(form.is_valid(), form.errors)

    def test_no_first_name_form(self):
        form = PersonForm(data=self.data, selected_person=False, no_first_name_checked=True)
        self.assertTrue(form.is_valid(), form.errors)
