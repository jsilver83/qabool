from django.utils.translation import ugettext_lazy as _

import os
from django.core.exceptions import ValidationError


# validates file extensions for uploaded documents
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.bmp', '.gif', '.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError(
            _('File extension (%(ext)s) not allowed!'),
            params={'ext': ext},
            code='ext_not_allowed',
        )


# validates image extensions for uploaded personal pictures
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.bmp', '.gif', '.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError(
            _('File extension (%(ext)s) not allowed!'),
            params={'ext': ext},
            code='ext_not_allowed',
        )


def is_eligible_for_housing(user):
    return user.get_student_phase() == 'ADMITTED' and user.eligible_for_housing


def is_eligible_for_roommate_search(user):
    return user.get_student_phase() == 'ADMITTED' and user.eligible_for_housing \
           and user.housing_user.searchable