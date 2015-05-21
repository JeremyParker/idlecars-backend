# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from settings import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "idlecars",
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

# Heap Analytics uses the DEBUG app id in development/testing
HEAP_APP_ID = '655181858'

WEBAPP_URL = 'http://localhost:3000'

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = ('localhost:3000',)

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}
