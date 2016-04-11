# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import os

from settings import *

# heap analytics tracking for production
HEAP_APP_ID = '3053705704'

DRIVER_APP_URL = 'http://app.idlecars.com'
OWNER_APP_URL = 'http://owner.idlecars.com'

ALLOWED_HOSTS = ['alltaxi.herokuapp.com']

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = (
    'app.idlecars.com',
    'app.idlecars.com.s3-website-us-east-1.amazonaws.com',
    'owner.idlecars.com',
    'owner.idlecars.com.s3-website-us-east-1.amazonaws.com',
)

SECRET_KEY = os.getenv('SECRET_KEY')

QUEUE_IMPLEMENTATION = 'RealQueue'
SMS_IMPLEMENTATION = 'TwilioRestClient'
TLC_DATA_IMPLEMENTATION = 'Socrata'

CSRF_COOKIE_SECURE = True  # if True, only sends the CSRF token over HTTPS
SESSION_COOKIE_SECURE = True  # if True, only sends session cookie over HTTPS

DEFAULT_FROM_EMAIL = 'bookings@idlecars.com'
OPS_EMAIL = 'support@idlecars.zendesk.com'
STREET_TEAM_EMAIL = 'streetteam@idlecars.com'

PAYMENT_GATEWAY_NAME = 'braintree'
BRAINTREE_BASE_URL = 'www.braintreegateway.com'
