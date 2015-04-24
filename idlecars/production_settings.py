# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from settings import *

# heap analytics tracking for production
HEAP_APP_ID = '3053705704'

# Allow cross origin requests from these domains
CORS_ORIGIN_WHITELIST = (
    'app.idlecars.com',
    'http://app.idlecars.com.s3-website-us-east-1.amazonaws.com/',
)
