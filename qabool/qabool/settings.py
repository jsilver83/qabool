"""
Django settings for qabool project.

Generated by 'django-admin startproject' using Django 1.9.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Development SECRET_KEY. Must be overridden in local_settings.py
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tzb6lrxanv9^ne46ig%u^l16-yzw6*v!s2kn2ien9v)@e21ja+'

DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'undergraduate_admission',
    'find_roommate',
    'reversion',
    'captcha',
    'floppyforms',

    'import_export',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'reversion.middleware.RevisionMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'qabool.middleware.force_default_language.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'qabool.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'qabool.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
     'default': {
         'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
         # 'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
         'TIMEOUT': 60,
         'OPTIONS': {
             'MAX_ENTRIES': 1000
         }
     }
    #'default': {
    #    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #    'LOCATION': '127.0.0.1:11211',
    #    'TIMEOUT': 60,
    #    'OPTIONS': {
    #        'MAX_ENTRIES': 1000
    #    }
    #}
}

LOGIN_URL = 'login'

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ar'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TIME_ZONE = 'Asia/Riyadh'

LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
    os.path.join(BASE_DIR, 'custom_locale'),
)


# Logging
# https://docs.djangoproject.com/en/1.9/topics/logging/
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

SESSION_COOKIE_AGE = 2400  # 40 mins
SESSION_SAVE_EVERY_REQUEST = True  # create "sliding" expiration

MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

EMAIL_HOST = 'mail.kfupm.edu.sa'
EMAIL_PORT = '587'
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True

ADMINS = [('joud', 'joud@kfupm.edu.sa'), ('Dr. Ahmad Khayyat', 'akhayyat@kfupm.edu.sa'), ('almaaesh', 'almaaesh@kfupm.edu.sa')]
SERVER_EMAIL = 'admissions@kfupm.edu.sa'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

AUTH_USER_MODEL = 'undergraduate_admission.User'

NOCAPTCHA = True
RECAPTCHA_USE_SSL = True

DISABLE_SMS = False
DISABLE_EMAIL = False
DISABLE_CAPTCHA = False

CAPTCHA_CHALLENGE_FUNCT = 'undergraduate_admission.utils.random_digit_challenge' # 'captcha.helpers.math_challenge'
# CAPTCHA_NOISE_FUNCTIONS = None
CAPTCHA_LETTER_ROTATION = (-10,10)

CSRF_FAILURE_VIEW = 'undergraduate_admission.views.general_views.csrf_failure'

MEDIA_URL = '/uploaded_docs/'

# Override settings using environment-specific settings, if any
try:
    from qabool.local_settings import *
except ImportError:
    print('local_settings.py not found')
