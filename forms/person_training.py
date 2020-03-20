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

from dal import autocomplete
from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from base.models.person import Person
from continuing_education.models.continuing_education_training import ContinuingEducationTraining
from continuing_education.models.enums.groups import TRAINING_MANAGERS_GROUP
from continuing_education.models.person_training import PersonTraining


class PersonTrainingForm(ModelForm):

    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=autocomplete.ModelSelect2(url='employee_autocomplete')
    )

    training = forms.ModelChoiceField(
        queryset=ContinuingEducationTraining.objects.all(),
        widget=autocomplete.ModelSelect2(url='training_autocomplete')
    )

    class Meta:
        model = PersonTraining

        fields = [
            'person',
            'training',
        ]

        # Automatic translation of field names
        labels = {field: _(field) for field in fields}

    def clean(self):
        try:
            PersonTraining.objects.get(person=self.cleaned_data['person'], training=self.cleaned_data['training'])
        except (PersonTraining.DoesNotExist, KeyError):
            pass
        else:
            raise ValidationError({'person': [_('Manager is already assigned on this training')]})
        if not self.cleaned_data['person'].user:
            raise ValidationError({'person': [_('Manager person has no user')]})
        return self.cleaned_data

    def save(self, commit=True):
        instance = super(PersonTrainingForm, self).save(commit=commit)
        instance.person.user.groups.add(Group.objects.get(name=TRAINING_MANAGERS_GROUP))
        return instance
