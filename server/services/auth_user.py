# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import string, random

from django.contrib.auth.models import User

user_param_keys = ['phone_number', 'email', 'first_name', 'last_name']

def create_auth_user(user_account):
    '''
    DEPRECATED
    '''
    password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
    auth_user = User.objects.create_user(
        username=user_account.phone_number,
        password=password,
        email=user_account.email,
        first_name=user_account.first_name,
        last_name=user_account.last_name,
    )
    return auth_user


def update(user, kwargs):
    if not set(kwargs.keys()).intersection(set(user_param_keys)):
        return
    user.username = kwargs.get('phone_number', user.username)
    user.email = kwargs.get('email', user.email)
    user.first_name = kwargs.get('first_name', user.first_name)
    user.last_name = kwargs.get('last_name', user.last_name)
    user.save()
