from django.utils.translation import ugettext_lazy as _

import os
from django.core.exceptions import ValidationError


MAX_IMAGE_UPLOAD_SIZE = 2000000
MAX_FILE_UPLOAD_SIZE = 2000000


def size_format(b):
    b = float(b)
    if b < 1000:
        return '%i' % b + 'B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b / 1000) + ' KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b / 1000000) + ' MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b / 1000000000) + ' GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b / 1000000000000) + ' TB'


valid_file_extensions = ['.pdf', '.bmp', '.gif', '.png', '.jpg', '.jpeg']


# validates file extensions for uploaded documents
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in valid_file_extensions:
        raise ValidationError(
            _('File extension (%(ext)s) not allowed!'),
            params={'ext': ext},
            code='ext_not_allowed',
        )

    if value.size > MAX_FILE_UPLOAD_SIZE:
        raise ValidationError(
            _('File size {} is larger than {}!'.format(size_format(value.size), size_format(MAX_FILE_UPLOAD_SIZE))),
            code='size_not_allowed',
        )


valid_image_extensions = ['.bmp', '.gif', '.png', '.jpg', '.jpeg']


# validates image extensions for uploaded personal pictures
def validate_image_extension(value):
    ext = os.path.splitext(value.name)[1].lower()

    if ext not in valid_image_extensions:
        raise ValidationError(
            _('File extension (%(ext)s) not allowed!'),
            params={'ext': ext},
            code='ext_not_allowed',
        )

    if value.size > MAX_IMAGE_UPLOAD_SIZE:
        raise ValidationError(
            _('Image size {} is larger than {}!'.format(size_format(value.size), size_format(MAX_IMAGE_UPLOAD_SIZE))),
            code='size_not_allowed',
        )


def get_accepted_extensions(file_type='IMAGE'):
    if file_type == 'IMAGE':
        valid_extensions = valid_image_extensions
    else:
        valid_extensions = valid_file_extensions

    accepted_extensions = ''
    for ext in valid_extensions:
        accepted_extensions += ext + ','

    return accepted_extensions
