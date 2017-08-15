from django.db.models.signals import post_save
from django.dispatch import receiver

from find_roommate.models import RoommateRequest
from undergraduate_admission.models import User
from undergraduate_admission.utils import SMS


@receiver(post_save, sender=User)
def student_post_withdrawal(sender, **kwargs):
    user = kwargs['instance']
    try:
        if user.status_message.status.status_code == 'WITHDRAWN':
            roommate_requests = RoommateRequest.objects.filter(requesting_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])

            print(roommate_requests)
            print(roommate_requests.first())
            # print(roommate_requests.first().requesting_user)
            # print(roommate_requests.first().requested_user)
            if roommate_requests.count():
                print('requesting_user with')
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTING_STUDENT_WITHDRAWN)
                SMS.send_sms_withdrawn(roommate_requests.first().requested_user.mobile)

            roommate_requests = RoommateRequest.objects.filter(requested_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])
            print(roommate_requests)
            print(roommate_requests.first())
            print(roommate_requests.first().pk)
            # print(roommate_requests.first().requesting_user)
            # print(roommate_requests.first().requested_user)
            print(roommate_requests.count())
            if roommate_requests.count():
                print('requested_user with')
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTED_STUDENT_WITHDRAWN)
                SMS.send_sms_withdrawn(roommate_requests.first().requesting_user.mobile)

    except AttributeError:  # staff users don't have status
        pass
