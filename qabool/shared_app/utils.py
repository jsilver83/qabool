from undergraduate_admission.models import AdmissionRequest


def get_current_admission_request_for_logged_in_user(request):
    if request.user.is_authenticated:
        admission_requests = AdmissionRequest.objects.filter(user=request.user, semester__active=True)

        if admission_requests:
            return admission_requests.first()
