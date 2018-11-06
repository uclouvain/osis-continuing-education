from django.contrib import admin
from continuing_education.models import admission, continuing_education_person,\
    address, file

admin.site.register(admission.Admission, admission.AdmissionAdmin)
admin.site.register(continuing_education_person.ContinuingEducationPerson, continuing_education_person.ContinuingEducationPersonAdmin)
admin.site.register(address.Address, address.AddressAdmin)
admin.site.register(file.File, file.FileAdmin)
