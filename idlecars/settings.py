# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

"""
Django settings for idlecars project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '+ij8@u%aj$ntf&hs$5%t!bb)(r1-qj7^kv58n@%iw5f8rj8+ii'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'server',
    'credit',
    'rest_framework',
    'rest_framework.authtoken',
    # 'website',
    'owner_crm',
    'unsubscribes',
    'django_nose',
    'djrill',
    'django_extensions',
    'addition',
    'removal',
)

MIDDLEWARE_CLASSES = (
    'sslify.middleware.SSLifyMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'idlecars.urls'

WSGI_APPLICATION = 'idlecars.wsgi.application'

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    # Parse database configuration from $DATABASE_URL
    'default': dj_database_url.config()
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'EST'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

APPEND_SLASH=False

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# mark pages with a 'nosniff' header to stop browsers trying to determine the MIME type themselves
SECURE_CONTENT_TYPE_NOSNIFF = True

# more CSRF security
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False  # if True, only sends the CSRF token over HTTPS

SESSION_COOKIE_SECURE = False  # if True, only sends session cookie over HTTPS

X_FRAME_OPTIONS = 'DENY'

# Allow all host headers
ALLOWED_HOSTS = ['*']

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
        }
    }
}

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "../idlecars/templates"),
)

TEMPLATE_LOADERS = (
    ('pyjade.ext.django.Loader',(
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django_settings_export.settings_export',
)

SETTINGS_EXPORT = [
    'STATIC_URL',
    'HEAP_APP_ID',
    'DRIVER_APP_URL',
    'OWNER_APP_URL',
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# default to the FakeSmsClient. Replace with TwilioRestClient to use Twilio
SMS_IMPLEMENTATION = 'FakeSmsClient'
TWILIO_PHONE_NUMBER = '+16466933874'
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'AC0f99e71e116ef18f0e8b2e67dcc28e97')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '19f726892e44c923f6c1c67f62d360cc')

MANDRILL_API_KEY = os.getenv('MANDRILL_APIKEY', '17bIyAXLhDzqG-At8DB3Nw') # if not in env, test_key
EMAIL_BACKEND = 'djrill.mail.backends.djrill.DjrillBackend'
DEFAULT_FROM_EMAIL = 'drivers@alltaxiny.com'
OPS_EMAIL = 'test@alltaxiny.com'
OPS_PHONE_NUMBER = '6469021306'

TLC_DATA_IMPLEMENTATION = 'TestClient' #'Socrata'
SOCRATA_APP_TOKEN = os.getenv('SOCRATA_APP_TOKEN', 'comes from environment')
SOCRATA_PASSWORD = os.getenv('SOCRATA_PASSWORD', 'comes from environment')
SOCRATA_USERNAME = 'alltaxi@jeremyparker.org'

# default to the FakeQueue, so we can run tests sychronously. Replace with RealQueue to use rq.
QUEUE_IMPLEMENTATION = 'FakeQueue'

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'cache-control',
    'accept-encoding',
    'dnt',
    'accept',
    'origin',
    'authorization',
    'x-csrftoken',
)

# Heap Analytics uses the DEBUG app id in development/testing
HEAP_APP_ID = '655181858'

PAYMENT_GATEWAY_NAME = 'fake'

STALENESS_LIMIT = 14
SIGNUP_CREDIT = 50
INVITOR_CREDIT = 50

ALLTAXI_PHONE_NUMBER = '(718) 361-0055'
