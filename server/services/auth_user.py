# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import string, random

from django.contrib.auth.models import User

def get_or_create_auth_user(user_account):
    try:
        return User.objects.get(username=user_account.phone_number)
    except User.DoesNotExist:
        password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
        auth_user = User.objects.create_user(
            username=user_account.phone_number,
            password=password,
            email=user_account.email,
            first_name=user_account.first_name,
            last_name=user_account.last_name,
        )
        return auth_user
