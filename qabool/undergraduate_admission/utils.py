import requests

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from qabool import settings
from undergraduate_admission.models import AdmissionSemester, Agreement


class Email(object):
    email_messages = {
        'registration_success':
            _('Dear %s,<br>Your request has been successfully submitted and the Admission results '
                'will be announced on Wednesday June 15, 2016 ... <br>'
                '<h4>Registration Details</h4><hr>'
                'Registration ID: %s<br>'
                'Mobile: %s<br>'
                'Registration Date: %s'
                'You agreed to the following:%s'
                '<hr>You are recommended to frequently visit the admission website to know the '
                'admission result and any updated instructions.<br><br> Admissions Office, King Fahd '
                'University of Petroleum and Minerals'),
    }

    @staticmethod
    def send_email_registration_success(user):
        sem = AdmissionSemester.get_phase1_active_semester()
        agreement = get_object_or_404(Agreement, agreement_type='INITIAL', semester=sem)
        agreement_items = agreement.items.all()

        html_message = Email.email_messages['registration_success']%(user.first_name,
                                                                     user.id,
                                                                     user.mobile,
                                                                     timezone.now().strftime('%x'),
                                                                     agreement.agreement_header)
        plain_message = Email.email_messages['registration_success']%(user.first_name, user.id, agreement.agreement_header)

        send_mail(_('KFUPM Admission'), plain_message,
                  'admissions@kfupm.edu.sa', [user.email], fail_silently=True,
                  html_message=html_message)


class SMS(object):
    sms_messages = {
        'registration_success': _('Your request has been successfully submitted and the Admission results will be '
                                  'announced on Wednesday June 24, 2015 (12:00 pm) ... '
                                  'Applicant is recommended to frequently visit the admission website to know the '
                                  'admission result and any updated instructions. Admissions Office, King Fahd '
                                  'University of Petroleum and Minerals'),
        'confirmation_message': _('TBA'),
    }

    @staticmethod
    def send_sms(mobile, body):
        r = requests.post('http://api.unifonic.com/rest/Messages/Send',
                          data = {'AppSid': settings.UNIFONIC_APP_SID,
                                  'Recipient': mobile,
                                  'Body': body,
                                  'SenderID': 'KFUPM-ADM'})
        return r

    @staticmethod
    def send_sms_registration_success(mobile):
        SMS.send_sms(mobile, SMS.sms_messages['registration_success'])

