"""
WSGI config for qabool project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

#from undergraduate_admission.models import RegistrationStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qabool.settings")

application = get_wsgi_application()

#RegistrationStatus.init_statuses()
