import requests

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from qabool import settings
from undergraduate_admission.models import AdmissionSemester, Agreement


class Email(object):
    email_messages = {
        'registration_success': _('Your request has been successfully submitted and the Admission results will be '
                                  'announced on Wednesday June 24, 2015 (12:00 pm) ... '
                                  'Applicant is recommended to frequently visit the admission website to know the '
                                  'admission result and any updated instructions. Admissions Office, King Fahd '
                                  'University of Petroleum and Minerals'),
    }

    @staticmethod
    def send_email_registration_success(email):
        sem = AdmissionSemester.get_phase1_active_semester()
        agreement = get_object_or_404(Agreement, agreement_type='INITIAL', semester=sem)
        agreement_items = agreement.items.all()

        send_mail('Subject here', SMS.sms_messages['registration_success'],
                  'admissions@kfupm.edu.sa', [email], fail_silently=True,
                  html_message=Email.email_messages['registration_success'] + agreement.agreement_header)


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

