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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import model_to_dict
from django.test import TestCase
from rest_framework import status

from base.tests.factories.person import PersonWithPermissionsFactory
from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.enums import admission_state_choices
from continuing_education.tests.factories.admission import AdmissionFactory


class ViewRegistrationTestCase(TestCase):
    def setUp(self):
        self.manager = PersonWithPermissionsFactory('can_access_admission', 'change_admission')
        self.client.force_login(self.manager.user)
        self.admission_accepted = AdmissionFactory(state=admission_state_choices.ACCEPTED)
        self.admission_rejected = AdmissionFactory(state=admission_state_choices.REJECTED)

    def test_list_registrations(self):
        url = reverse('registration')
        response = self.client.get(url)
        admissions = response.context['admissions']
        for admission in admissions:
            self.assertEqual(admission.state, admission_state_choices.ACCEPTED)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registrations.html')

    def test_list_registrations_pagination_empty_page(self):
        url = reverse('registration')
        response = self.client.get(url, {'page': 0})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registrations.html')

    def test_registration_detail(self):
        url = reverse('registration_detail', args=[self.admission_accepted.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration_detail.html')

    def test_registration_detail_not_found(self):
        response = self.client.get(reverse('registration_detail', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_registration_edit_not_found(self):
        response = self.client.get(reverse('registration_edit', kwargs={
            'admission_id': 0,
        }))
        self.assertEqual(response.status_code, 404)

    def test_edit_get_registration_found(self):
        url = reverse('registration_edit', args=[self.admission_accepted.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration_form.html')

    def test_edit_post_registration_found(self):
        admission = AdmissionFactory()
        admission_dict = model_to_dict(admission)
        admission_dict['billing_address'] = admission.billing_address
        admission_dict['residence_address'] = admission.residence_address
        admission_dict['citizenship'] = admission.citizenship
        admission_dict['address'] = admission.address
        url = reverse('registration_edit', args=[self.admission_accepted.id])
        form = RegistrationForm(admission_dict)
        form.is_valid()
        response = self.client.post(url, data=form.cleaned_data)
        self.assertRedirects(response, reverse('registration_detail', args=[self.admission_accepted.id]))
        self.admission_accepted.refresh_from_db()

        # verifying that fields are correctly updated
        for key in form.cleaned_data.keys():
            field_value = self.admission_accepted.__getattribute__(key)
            self.assertEqual(field_value, admission_dict[key])

    def test_registration_list_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('registration')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_detail_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('registration_detail', kwargs={'admission_id':self.admission_accepted.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_registration_edit_unauthorized(self):
        unauthorized_user = User.objects.create_user('unauthorized', 'unauth@demo.org', 'passtest')
        self.client.force_login(unauthorized_user)
        url = reverse('registration_edit', kwargs={'admission_id': self.admission_accepted.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)