import os
from django.utils import timezone


def upload_location_govid(instance, filename):
    return upload_location('govid', instance, filename)


def upload_location_birth(instance, filename):
    return upload_location('birth', instance, filename)


def upload_location_mother_govid(instance, filename):
    return upload_location('mother_govid', instance, filename)


def upload_location_passport(instance, filename):
    return upload_location('passport', instance, filename)


def upload_location_certificate(instance, filename):
    return upload_location('certificate', instance, filename)


def upload_location_courses(instance, filename):
    return upload_location('certificate/courses', instance, filename)


def upload_location_picture(instance, filename):
    return upload_location('picture', instance, filename)


# defines where to save uploaded student documents
def upload_location(sub_folder, instance, filename):
    upload_date = timezone.now().strftime('%d-%m-%Y')
    ext = os.path.splitext(filename)[1]
    if instance.kfupm_id:
        return '%s/%s/%s%s'%(sub_folder, upload_date, instance.kfupm_id, ext)
    else:
        return '%s/%s/%s%s'%(sub_folder, upload_date, instance.username, ext)