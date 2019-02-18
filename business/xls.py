from django.utils.translation import ugettext_lazy as _

from base.business.xls import get_name_or_username
from osis_common.document import xls_build


ADMISSION_TITLES = [
    str(_('Name')),
    str(_('First name')),
    str(_('Email')),
    str(_('Formation')),
    str(_('Faculty')),
    str(_('State')),
    ]

XLS_DESCRIPTION = _('Admissions list')
XLS_FILENAME = _('Admissions_list')
WORKSHEET_TITLE = _('Admissions list')


def create_xls(user, admission_list, form):
    filters = _form_filters(form)

    working_sheets_data = prepare_xls_content(admission_list)
    parameters = {xls_build.DESCRIPTION: XLS_DESCRIPTION,
                  xls_build.USER: get_name_or_username(user),
                  xls_build.FILENAME: XLS_FILENAME,
                  xls_build.HEADER_TITLES: ADMISSION_TITLES,
                  xls_build.WS_TITLE: WORKSHEET_TITLE}

    return xls_build.generate_xls(xls_build.prepare_xls_parameters_list(working_sheets_data, parameters), filters)


def prepare_xls_content(admission_list):
    return [extract_xls_data_from_admission(admission) for admission in admission_list]


def extract_xls_data_from_admission(admission):
    return [
        admission.person_information.person.first_name,
        admission.person_information.person.last_name,
        admission.email,
        admission.formation,
        admission.get_faculty() if admission.get_faculty() else '',
        _(admission.state) if admission.state else ''
    ]


def _form_filters(form):
    criteria = {}
    if form:
        for field_name, field in form.fields.items():
            if form.cleaned_data[field_name]:
                criteria[field.label] = form.cleaned_data[field_name]

    return criteria
