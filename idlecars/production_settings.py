# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os

from settings import *

# heap analytics tracking for production
HEAP_APP_ID = '3053705704'

DRIVER_APP_URL = 'http://app.alltaxi.com.s3-website-us-east-1.amazonaws.com'
OWNER_APP_URL = 'http://owner.alltaxi.com.s3-website-us-east-1.amazonaws.com'

ALLOWED_HOSTS = ['alltaxi.herokuapp.com']

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = (
    'app.alltaxi.com.s3-website-us-east-1.amazonaws.com',
    'owner.alltaxi.com.s3-website-us-east-1.amazonaws.com',
)

SECRET_KEY = os.getenv('SECRET_KEY')

QUEUE_IMPLEMENTATION = 'RealQueue'
SMS_IMPLEMENTATION = 'TwilioRestClient'
TLC_DATA_IMPLEMENTATION = 'Socrata'

# We're not using SSL at the moment. No payments happening.
SSLIFY_DISABLE = True
CSRF_COOKIE_SECURE = False  # if True, only sends the CSRF token over HTTPS
SESSION_COOKIE_SECURE = False  # if True, only sends session cookie over HTTPS

DEFAULT_FROM_EMAIL = 'drivers@alltaxiny.com'
OPS_EMAIL =  'jeremy@idlecars.com'

PAYMENT_GATEWAY_NAME = 'braintree'
BRAINTREE_BASE_URL = 'www.braintreegateway.com'
