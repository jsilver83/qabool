import random
from itertools import islice

import requests
from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from markdown2 import Markdown
from zeep import Client
from zeep import Transport

from undergraduate_admission.models import *


class Email(object):
    email_messages = {
        'registration_success':
            _('Dear %(student_name)s,<br>Your request has been successfully submitted<br>'
              '<h4>Registration Details</h4><hr>'
              # 'Registration ID: %(user_id)s<br>'
              'Name: %(student_name)s<br>'
              'Mobile: %(mobile)s<br>'
              'Registration Date: %(reg_date)s<br><hr><br>'
              'We appreciate your feedback: <a href="http://www.kfupm.edu.sa/departments/admissions/SitePages/ar/Survey.aspx">http://www.kfupm.edu.sa/departments/admissions/SitePages/ar/Survey.aspx</a> . <br><hr><br>'
              'You agreed to the following:<br>%(agreement)s'
              '<br><br> Admissions Office, <br>King Fahd '
              'University of Petroleum and Minerals'),
        'registration_success_old_high_school': _('Dear %(student_name)s,<br>We regret to inform you that your '
                                                  'application has been rejected because your old high school '
                                                  'certificate. '
                                                  '<h4>Registration Details</h4><hr>'
                                                  # 'Registration ID: %(user_id)s<br>'
                                                  'Mobile: %(mobile)s<br>'
                                                  'Registration Date: %(reg_date)s<br><hr><br>'
                                                  'You agreed to the following:<br>%(agreement)s'
                                                  '<hr><br>'
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
        if user.student_type == 'N':
            agreement = get_object_or_404(Agreement, agreement_type=Agreement.AgreementTypes.INITIAL,
                                          status_message=RegistrationStatus.get_status_applied_non_saudi(),
                                          semester=sem)
        else:
            agreement = get_object_or_404(Agreement, agreement_type=Agreement.AgreementTypes.INITIAL,
                                          status_message=RegistrationStatus.get_status_applied(),
                                          semester=sem)
        markdown_maker = Markdown()
        agreement_html = markdown_maker.convert(agreement.agreement)

        html_message = Email.email_messages['registration_success'] % (
            {'student_name': user.get_student_full_name(),
             # 'student_name': user.first_name,
             'user_id': user.id,
             'mobile': user.mobile,
             'reg_date': user.request_date,
             'agreement': agreement_html,
             })

        if user.status_message == RegistrationStatus.get_status_old_high_school():
            plain_message = SMS.sms_messages['registration_success_old_high_school']
        else:
            plain_message = SMS.sms_messages['registration_success']

        if settings.DISABLE_EMAIL:
            return None

        try:
            send_mail(_('KFUPM Admission'), plain_message,
                      settings.EMAIL_HOST_USER, [user.user.email], fail_silently=True,
                      html_message=html_message)
        except:  # usually TimeoutError but made it general so it will never raise an exception
            pass


class SMS(object):
    sms_messages = {
        'registration_success': _(
            'Your request was submitted. Share feedback http://www.kfupm.edu.sa/departments/admissions/SitePages/ar/Survey.aspx, KFUPM'),
        'registration_success_old_high_school': _('Application was rejected '
                                                  'because of old HS certificate. '
                                                  'Share feedback: http://www.kfupm.edu.sa/departments/admissions/SitePages/ar/Survey.aspx.'
                                                  'KFUPM'),
        'partial_admission_message': _('Congrats, you have been admitted into KFUPM. Check our website'),
        'general_results_message': _('Your admission result is out. Check our website. KFUPM'),
        'confirmed_message': _('Documents were submitted and being checked. Check website later. KFUPM'),
        'docs_issue_message': _('You have issues in documents. Check website to fix them. KFUPM'),
        'admitted_msg':
            _('Your admission is confirmed. Check website to print admission letter. KFUPM'),
        'withdrawn_msg':
            _('Your admission was withdrawn as per your request. Good luck. KFUPM'),
        'housing_roommate_request_sent':
            _('You received a roommate request. Login to our site to accept. Student housing'),
        'housing_roommate_request_accepted':
            _('Your roommate request was accepted. Login to our site to print docs. Student housing'),
        'housing_roommate_request_rejected':
            _('Your roommate request was rejected. Login to our site to send another one. Student housing'),
        'housing_roommate_request_withdrawn':
            _('Your roommate has withdrawn. Login to our site to search for another roommate. Student housing'),
        'housing_rooms_threshold_100':
            _('Remaining rooms is 100'),
        'housing_rooms_threshold_50':
            _('Remaining rooms is 50'),
        'housing_rooms_threshold_10':
            _('Remaining rooms is 10'),
        'sms_tarifi_week':
            _('Dear Student:\nKindly login to https://qabool.kfupm.edu.sa to view your Tarifi Week schedule.\n'
              'And You have to bring the printed schedule in addition to your admission letter'
              '\nStudent Affairs\nKFUPM')
    }

    # using UNIFONIC gateway to send SMS
    @staticmethod
    def send_sms(mobile, body):
        if settings.DISABLE_SMS:
            return None

        try:
            r = requests.post('http://api.unifonic.com/rest/Messages/Send',
                              data={'AppSid': settings.UNIFONIC_APP_SID,
                                    'Recipient': mobile,
                                    'Body': body,
                                    'SenderID': 'KFUPMQabool'})  # It was KFUPM-ADM
            return r
        except:  # usually TimeoutError but made it general so it will never raise an exception
            pass

    @staticmethod
    def send_mass_sms(mobiles, body):
        if settings.DISABLE_SMS:
            return None

        mobiles_chunked = chunk(mobiles, 999)

        for mobiles_chunk in mobiles_chunked:
            recipients = list_to_comma_separated_string_value(mobiles_chunk)

            try:
                r = requests.post('http://api.unifonic.com/rest/Messages/SendBulk',
                                  data={'AppSid': settings.UNIFONIC_APP_SID,
                                        'Recipient': recipients,
                                        'Body': body,
                                        'SenderID': 'KFUPMQabool'})  # It was KFUPM-ADM
                return r
            except:  # usually TimeoutError but made it general so it will never raise an exception
                pass

    # using Yesser Tarasol service to send SMS
    @staticmethod
    def send_sms_deprecated(mobile, body):
        if settings.DISABLE_SMS:
            return None

        try:
            client = Client(settings.YESSER_SMS_WSDL, transport=Transport(timeout=5))
            sms_type = client.get_type('ns2:SMSNotificationStructure')
            new_sms = sms_type(Requestor='KFUPMQabool',
                               Message=body,
                               LineNumber=mobile,
                               NotificationId='225656')
            result = client.service.SendNotification(new_sms)
            return result
        except:  # ERROR: Client request message schema validation failure
            pass

    @staticmethod
    def send_sms_registration_success(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['registration_success']))

    @staticmethod
    def send_sms_registration_success_old_high_school(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['registration_success_old_high_school']))

    @staticmethod
    def send_sms_confirmed(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['confirmed_message']))

    @staticmethod
    def send_sms_admitted(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['admitted_msg']))

    @staticmethod
    def send_sms_docs_issue_message(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['docs_issue_message']))

    @staticmethod
    def send_sms_withdrawn(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['withdrawn_msg']))

    @staticmethod
    def send_sms_housing_roommate_request_sent(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['housing_roommate_request_sent']))

    @staticmethod
    def send_sms_housing_roommate_request_accepted(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['housing_roommate_request_accepted']))

    @staticmethod
    def send_sms_housing_roommate_request_rejected(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['housing_roommate_request_rejected']))

    @staticmethod
    def send_sms_housing_roommate_request_withdrawn(mobile):
        SMS.send_sms(mobile, '%s' % (SMS.sms_messages['housing_roommate_request_withdrawn']))

    @staticmethod
    def send_sms_housing_rooms_threshold_100():
        SMS.send_sms('966505932317', '%s' % (SMS.sms_messages['housing_rooms_threshold_100']))
        SMS.send_sms('966569402303', '%s' % (SMS.sms_messages['housing_rooms_threshold_100']))

    @staticmethod
    def send_sms_housing_rooms_threshold_50():
        SMS.send_sms('966505932317', '%s' % (SMS.sms_messages['housing_rooms_threshold_50']))
        SMS.send_sms('966569402303', '%s' % (SMS.sms_messages['housing_rooms_threshold_50']))

    @staticmethod
    def send_sms_housing_rooms_threshold_10():
        SMS.send_sms('966505932317', '%s' % (SMS.sms_messages['housing_rooms_threshold_10']))
        SMS.send_sms('966569402303', '%s' % (SMS.sms_messages['housing_rooms_threshold_10']))

    @staticmethod
    def send_mass_sms_tarifi_week(mobiles):
        print(SMS.sms_messages['sms_tarifi_week'])
        SMS.send_mass_sms(mobiles, SMS.sms_messages['sms_tarifi_week'])


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


# convert strings with non standard numerals to standard numerals while preserving initial zeroes
# like ۰۰۰۱ or ٠٠٠١ or ໐໐໐໑ will be converted to 0001
def parse_non_standard_numerals(str_numerals):
    # print(str_numerals)
    if str_numerals:
        new_string = ''
        for single_char in str_numerals:
            new_string += str(try_parse_int(single_char))

        return new_string
    else:
        return ''


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class PlainTextWidget(forms.Widget):
    def render(self, name, value, attrs=None):
        if value is not None:
            field = "<input type='hidden' name='%s' value='%s' readonly> <span>%s</span>" \
                    % (name, mark_safe(value), mark_safe(value))
        else:
            field = "<input type='hidden' name='%s' value='' readonly> <span>-</span>" % (name)
        return field


def format_date_time(date_time):
    return timezone.localtime(date_time).strftime('%d-%m-%Y %I:%M %p')


def format_date_time_verbose(date_time):
    return timezone.localtime(date_time).strftime('%d %B %Y %I:%M %p')


def format_date(date_time):
    return timezone.localtime(date_time).strftime('%d-%m-%Y')


def format_time(date_time):
    return timezone.localtime(date_time).strftime('%I:%M %p')


def add_validators_to_arabic_and_english_names(fields):
    for field in fields:
        if field.name in ['student_full_name_en', 'first_name_en', 'second_name_en', 'third_name_en',
                          'family_name_en']:
            field.validators += [
                RegexValidator(
                    r'^[A-Za-z.\- ]+$',
                    message=_("Use English alphabet only! You can also use the dot, hyphen and spaces")
                ), ]
            if len(field.validators) > 2:
                field.validators.pop(len(field.validators) - 1)

        elif field.name in ['student_full_name_ar', 'first_name_ar', 'second_name_ar', 'third_name_ar',
                            'family_name_ar']:
            field.validators += [
                RegexValidator(
                    r'^[\u0600-\u06FF ]+$',
                    message=_("Use Arabic alphabet only! You can also use spaces and diacritics (tashkil)")
                ), ]
            if len(field.validators) > 2:
                field.validators.pop(len(field.validators) - 1)


def concatenate_names(*args, allow_hyphen=False, trim_spaces=True):
    concatenated_names = ''
    for name in args:
        if name and name.strip() == '-' and not allow_hyphen:
            continue
        if name:
            if trim_spaces:
                concatenated_names += name.strip() + ' '
            else:
                concatenated_names += name + ' '

    return concatenated_names[:len(concatenated_names) -1]


def get_field_field_name_from_short_type(short_file_type):
    return {
        'withdrawal_proof': 'withdrawal_proof',
        'govid': 'government_id_file',
        'birth': 'birth_certificate',
        'mother_govid': 'mother_gov_id_file',
        'passport': 'passport_file',
        'certificate': 'high_school_certificate',
        'certificate/courses': 'courses_certificate',
        'picture': 'personal_picture',
        'driving_license': 'driving_license_file',
        'vehicle_registration': 'vehicle_registration_file',
        'bank_account': 'bank_account_identification_file',
    }[short_file_type]


def get_fields_for_re_upload(student_type):
    fields = ['government_id_file', 'personal_picture', 'high_school_certificate', 'courses_certificate', ]

    if student_type in ['M', 'N']:
        fields.append('passport_file')

    if student_type == 'M':
        fields.extend(['mother_gov_id_file', 'birth_certificate', ])

    return fields


def list_to_comma_separated_string_value(list_to_converted):
    return ','.join(map(str, list_to_converted))


def chunk(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def check_overlap_between_two_date_ranges(range1_start, range1_end, range2_start, range2_end):
    from collections import namedtuple
    Range = namedtuple('Range', ['start', 'end'])

    r1 = Range(start=range1_start, end=range1_end)
    r2 = Range(start=range2_start, end=range2_end)
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start).days + 1
    overlap = max(0, delta)
    return overlap > 0
