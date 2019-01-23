import os
from django.conf import settings
from django.utils import timezone


def upload_location_withdrawal_proof(instance, filename):
    return upload_location('withdrawal_proof', instance, filename)


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


def upload_location_driving_license(instance, filename):
    return upload_location('driving_license', instance, filename)


def upload_location_vehicle_registration(instance, filename):
    return upload_location('vehicle_registration', instance, filename)


def upload_bank_account_identification(instance, filename):
    return upload_location('bank_account', instance, filename)


# defines where to save uploaded student documents
def upload_location(sub_folder, instance, filename):
    semester_name = instance.semester.semester_name
    if sub_folder == 'picture':
        ext = '.jpg'  # personal picture will always come in jpg format from cropper.js
    else:
        ext = os.path.splitext(filename)[1]
    file_name = '%s/%s/%s%s'%(sub_folder, semester_name, instance.user.username, ext)
    full_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if os.path.exists(full_path):
        os.remove(full_path)
    return file_name
