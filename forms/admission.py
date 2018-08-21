from django.forms import ModelForm

from base.forms.bootstrap import BootstrapModelForm
from continuing_education.models.admission import Admission
from django.utils.translation import ugettext_lazy as _
from django import forms

class AdmissionForm(ModelForm):
    high_school_diploma = forms.TypedChoiceField(coerce=lambda x: x =='True',
                                   choices=((False, _('No')), (True, _('Yes'))))

    class Meta:
        model = Admission
        fields = "__all__"