# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "alltaxi",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
SSLIFY_DISABLE = True

DRIVER_APP_URL = 'http://localhost:3000'
OWNER_APP_URL = 'http://localhost:3001'

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = ('localhost:3000','localhost:3001',)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
}

STALENESS_LIMIT = 180
