import os

import random
import requests
from django.core.exceptions import ValidationError

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from qabool import settings
from undergraduate_admission.models import Agreement, AdmissionSemester


class Email(object):
    email_messages = {
        'registration_success':
            _('Dear %(student_name)s,<br>Your request has been successfully submitted and the Admission results '
              'will be announced on Wednesday June 15, 2016 ... <br>'
              '<h4>Registration Details</h4><hr>'
              'Registration ID: %(user_id)s<br>'
              'Mobile: %(mobile)s<br>'
              'Registration Date: %(reg_date)s<br><hr><br>'
              'You agreed to the following:<br>%(agree_header)s<br><br><ul>%(agree_items)s</ul>'
              '<hr><br>'
              # 'You are recommended to frequently visit the admission website to know the '
              # 'admission result and any updated instructions.'
              'We appreciate your feedback: <a href="http://goo.gl/erw8HQ">http://goo.gl/erw8HQ</a> . '
              '<br><br> Admissions Office, <br>King Fahd '
              'University of Petroleum and Minerals'),
        # TODO: implement
        'admitted_msg':
            _('Dear Student, You have been admitted successfully and you have to attend the orientation'
              'week as specified in the admission letter'),
        # TODO: implement
        'withdrawn_msg':
            _('Dear Student, Your application has been withdrawn as per your request. We wish you luck '
              'in your future...'),
    }

    @staticmethod
    def send_email_registration_success(user):
        sem = AdmissionSemester.get_phase1_active_semester()
        agreement = get_object_or_404(Agreement, agreement_type='INITIAL', semester=sem)
        agreement_items = agreement.items.all()

        a_items = ''
        for a_item in agreement_items:
            a_items += '<li>%s</li>' % (a_item)

        html_message = Email.email_messages['registration_success'] % (
            {'student_name': user.first_name,
             'user_id': user.id,
             'mobile': user.mobile,
             'reg_date': timezone.now().strftime('%x'),
             'agree_header': agreement.agreement_header,
             'agree_items': a_items,
             })

        plain_message = SMS.sms_messages['registration_success']

        if settings.DISABLE_EMAIL:
            return None

        send_mail(_('KFUPM Admission'), plain_message,
                  'admissions@kfupm.edu.sa', [user.email], fail_silently=True,
                  html_message=html_message)


class SMS(object):
    sms_messages = {
        'registration_success': _('Your request has been successfully submitted. '
                                  'We appreciate your feedback:\nhttp://goo.gl/erw8HQ .\n'
                                  'Admissions Office, KFUPM'),
        'confirmation_message': _('TBA'),
        'admitted_msg':
            _('Dear Student, You have been admitted successfully and you have to attend the orientation'
              'week as specified in the admission letter'),
        'withdrawn_msg':
            _('Dear Student, Your application has been withdrawn as per your request. We wish you luck '
              'in your future...'),
    }

    @staticmethod
    def send_sms(mobile, body):
        if settings.DISABLE_SMS:
            return None

        r = requests.post('http://api.unifonic.com/rest/Messages/Send',
                          data={'AppSid': settings.UNIFONIC_APP_SID,
                                'Recipient': mobile,
                                'Body': body,
                                'SenderID': 'KFUPM-ADM'})
        return r

    @staticmethod
    def send_sms_registration_success(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['registration_success']))  # unjustifiable workaround

    @staticmethod
    def send_sms_admitted(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['admitted_msg']))

    @staticmethod
    def send_sms_withdrawn(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['withdrawn_msg']))


# a custom function to generate 6-digit captcha codes
def random_digit_challenge():
    ret = u''
    for i in range(6):
        ret += str(random.randint(0, 9))
    return ret, ret


# safe parsing of integers
def try_parse_int(str_to_int):
    try:
        return int(str_to_int)
    except:
        return -1

# safe parsing of floats
def try_parse_float(str_to_float):
    try:
        return float(str_to_float)
    except:
        return 0.0