##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import ugettext_lazy as _

PROGRAM_COMPLETE_PART1 = _('The programme is already complete')
PROGRAM_COMPLETE_PART2 = _('We will contact you again for the next edition')

VERIFICATION_IN_PROGRESS_PART1 = _('Your admission file is being verified by the responsible training jury')
VERIFICATION_IN_PROGRESS_PART2 = _('We will report to you as soon as possible')

PROGRAM_COMPLETE = "{}. {}.".format(PROGRAM_COMPLETE_PART1, PROGRAM_COMPLETE_PART2)
VERIFICATION_IN_PROGRESS = "{}. {}.".format(VERIFICATION_IN_PROGRESS_PART1, VERIFICATION_IN_PROGRESS_PART2)
OTHER = _('Other')

WAITING_REASON_CHOICES = (
    (PROGRAM_COMPLETE, PROGRAM_COMPLETE),
    (VERIFICATION_IN_PROGRESS, VERIFICATION_IN_PROGRESS),
    (OTHER, OTHER),
)


WAITING_REASON_CHOICES_SHORTENED_DISPLAY = (
    (PROGRAM_COMPLETE, PROGRAM_COMPLETE_PART1),
    (VERIFICATION_IN_PROGRESS, VERIFICATION_IN_PROGRESS_PART1),
    (OTHER, OTHER),
)
