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

# Heap Analytics uses the DEBUG app id in development/testing
HEAP_APP_ID = '655181858'

WEBAPP_URL = 'localhost:3000'

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = ('localhost:3000',)
