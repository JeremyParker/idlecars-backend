# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os

from settings import *

# heap analytics tracking for production
HEAP_APP_ID = '3053705704'

WEBAPP_URL = 'http://app.idlecars.com'

ALLOWED_HOSTS = ['www.idlecars.com']

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = (
    'app.idlecars.com',
    'app.idlecars.com.s3-website-us-east-1.amazonaws.com',
)

SECRET_KEY = os.getenv('SECRET_KEY')

QUEUE_IMPLEMENTATION = 'RealQueue'

CSRF_COOKIE_SECURE = True  # if True, only sends the CSRF token over HTTPS
SESSION_COOKIE_SECURE = True  # if True, only sends session cookie over HTTPS

DEFAULT_FROM_EMAIL = 'support@idlecars.com'
OPS_EMAIL = 'support@idlecars.com'

PAYMENT_GATEWAY_NAME = 'braintree'
