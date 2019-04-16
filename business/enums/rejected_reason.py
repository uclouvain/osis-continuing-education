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
from django.utils.translation import ugettext_lazy as _

COURSE_NOT_ADAPTED_TO_PROGRAM = _('Your course is not adapted to the program of this training')
DONT_MEET_ADMISSION_REQUIREMENTS = _('You do not meet the admission requirements')
PROGRAM_COMPLETE = _('The programme is already complete')
NOT_ENOUGH_EXPERIENCE = _('You do not have the experience and/or motivation to follow this program')
OTHER = _('Other')

REJECTED_REASON_CHOICES = (
    (COURSE_NOT_ADAPTED_TO_PROGRAM, COURSE_NOT_ADAPTED_TO_PROGRAM),
    (DONT_MEET_ADMISSION_REQUIREMENTS, DONT_MEET_ADMISSION_REQUIREMENTS,),
    (PROGRAM_COMPLETE, PROGRAM_COMPLETE),
    (NOT_ENOUGH_EXPERIENCE, NOT_ENOUGH_EXPERIENCE),
    (OTHER, OTHER),
)
