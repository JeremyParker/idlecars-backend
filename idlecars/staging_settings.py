# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from settings import *

# heap analytics tracking for staging
HEAP_APP_ID = '1900221263'

WEBAPP_URL = 'app.staging.idlecars.com'

ALLOWED_HOSTS = ['staging.idlecars.com']

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = (
    'app.staging.idlecars.com.s3-website-us-east-1.amazonaws.com',
    'app.staging.idlecars.com',
)
