# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "idlecars_test",
        "USER": "",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "",
    }
}

DEBUG = False
SSLIFY_DISABLE = True

WEBAPP_URL = 'localhost:3000'

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = ('localhost:3000',)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}

WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY = True
