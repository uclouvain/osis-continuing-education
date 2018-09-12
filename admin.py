from django.contrib import admin
from continuing_education.models import admission, person, address

admin.site.register(admission.Admission, admission.AdmissionAdmin)
admin.site.register(person.Person, person.PersonAdmin)
admin.site.register(address.Address, address.AddressAdmin)
