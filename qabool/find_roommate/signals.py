from django.db.models.signals import post_save
from django.dispatch import receiver

from find_roommate.models import RoommateRequest
from undergraduate_admission.models import User
from undergraduate_admission.utils import SMS


# TODO: Revise this signal and whether it should be here or in the withdraw page
@receiver(post_save, sender=User)
def student_post_withdrawal(sender, **kwargs):
    user = kwargs['instance']
    try:
        if user.status_message.status.status_code == 'WITHDRAWN':
            roommate_requests = RoommateRequest.objects.filter(requesting_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])

            if roommate_requests.count():
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTING_STUDENT_WITHDRAWN)
                for roommate_request in roommate_requests:
                    SMS.send_sms_withdrawn(roommate_request.requested_user.mobile)

            roommate_requests = RoommateRequest.objects.filter(requested_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])
            if roommate_requests.count():
                roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTED_STUDENT_WITHDRAWN)
                for roommate_request in roommate_requests:
                    SMS.send_sms_withdrawn(roommate_request.requesting_user.mobile)

    except AttributeError:  # staff users don't have status
        pass
