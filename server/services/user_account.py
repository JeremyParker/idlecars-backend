# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import server.models.user_account

def find_or_create(user_account_data):
    '''
    Finds an existing UserAccount if one exists, and updates its data.
    Creates a new UserAccount if none exists with the given email address.

    arguments:
    - user_account_data: an OrderedDict of user data as returned from validated_data
    in a serializer.
    '''
    try:
        user_account = server.models.user_account.UserAccount.objects.get(email=user_account_data['email'])
        for attr in user_account_data:
            setattr(user_account, attr, user_account_data[attr])
    except server.models.user_account.UserAccount.DoesNotExist:
        user_account = server.models.user_account.UserAccount.objects.create(**user_account_data)

    return user_account
