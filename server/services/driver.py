# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Driver

def find_or_create(user_account):
    '''
    Finds an existing Driver for this user_account if one exists, and returns it.
    Creates a new Driver if none exists with the given user_account.

    arguments:
    - user_account: an instance of models.UserAccount
    '''
    try:
        return Driver.objects.get(user_account=user_account)
    except Driver.DoesNotExist:
        return Driver.objects.create(user_account=user_account)
