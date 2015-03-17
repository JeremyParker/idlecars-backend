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
