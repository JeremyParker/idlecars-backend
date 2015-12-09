# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

class ServiceError(Exception):
    '''
    Generic exception that we can use for all services. The message should be returned to the
    user by the API layer.
    '''
    pass
