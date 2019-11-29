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
from django.core.validators import FileExtensionValidator
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext as _


class TooManyFilesException(Exception):
    def __init__(self, max_count=None, errors=None):
        message = _("The maximum number of files has been reached : maximum %(max)s files allowed.") % {
            'max': max_count
        }
        super(TooManyFilesException, self).__init__(message)
        self.errors = errors


class TooLongFilenameException(Exception):
    def __init__(self, max_length=None, errors=None):
        message = _("The name of the file is too long : maximum %(length)s characters.") % {'length': max_length}
        super(TooLongFilenameException, self).__init__(message)
        self.errors = errors


class TooLargeFileSizeException(Exception):
    def __init__(self, size=None, max_size=None, errors=None):
        message = _("File is too large (%(file_size)s) : maximum upload size allowed is %(max_size)s.") % {
            'file_size': filesizeformat(size),
            'max_size': filesizeformat(max_size)
        }
        super(TooLargeFileSizeException, self).__init__(message)
        self.errors = errors


class InvalidFileCategoryException(Exception):
    def __init__(self, errors=None):
        message = _("The status of the admission must be Accepted to upload an invoice.")
        super(InvalidFileCategoryException, self).__init__(message)
        self.errors = errors


class UnallowedFileExtensionException(Exception):
    def __init__(self, errors=None, extension=None, allowed_extensions=None):
        message = FileExtensionValidator.message % {
            'extension': extension,
            'allowed_extensions': ', '.join(allowed_extensions)
        }
        super(UnallowedFileExtensionException, self).__init__(message)
        self.errors = errors
