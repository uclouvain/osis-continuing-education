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
from django import forms
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models.person import Person
from continuing_education.forms.common import set_participant_required_fields

ADMISSION_PARTICIPANT_REQUIRED_FIELDS = [
    'first_name', 'last_name', 'gender',
]


class PersonForm(ModelForm):
    gender = forms.ChoiceField(
        choices=Person.GENDER_CHOICES,
    )

    def __init__(self, no_first_name_checked, *args, **kwargs):

        super(PersonForm, self).__init__(*args, **kwargs)

        set_participant_required_fields(self.fields,
                                        ADMISSION_PARTICIPANT_REQUIRED_FIELDS,
                                        True)

        self.fields['gender'].initial = Person.GENDER_CHOICES[2]
        if no_first_name_checked:
            self.fields['first_name'].required = False

    class Meta:
        model = Person

        fields = [
            'first_name',
            'last_name',
            'email',
            'gender'
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}
