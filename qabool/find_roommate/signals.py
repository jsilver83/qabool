from django.db.models.signals import post_save
from django.dispatch import receiver

from find_roommate.models import RoommateRequest
from undergraduate_admission.models import User


@receiver(post_save, sender=User)
def student_post_withdrawal(sender, **kwargs):
    user = kwargs['instance']
    try:
        if user.status_message.status.status_code == 'WITHDRAWN':
            roommate_requests = RoommateRequest.objects.filter(requesting_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])
            roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTING_STUDENT_WITHDRAWN)

            roommate_requests = RoommateRequest.objects.filter(requested_user=user,
                                                               status__in=[
                                                                   RoommateRequest.RequestStatuses.PENDING,
                                                                   RoommateRequest.RequestStatuses.ACCEPTED])
            roommate_requests.update(status=RoommateRequest.RequestStatuses.REQUESTED_STUDENT_WITHDRAWN)
    except AttributeError:  # staff users don't have status
        pass
