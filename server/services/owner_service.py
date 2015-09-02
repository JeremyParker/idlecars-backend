# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree
import random
import string

from django.conf import settings
from django.contrib.auth.models import User

from owner_crm.services import password_reset_service

from server.models import Owner, UserAccount
from server.services import auth_user as auth_user_service
from server import payment_gateways


def add_merchant_id_to_owner(merchant_account_id, owner):
    owner.merchant_id = merchant_account_id
    owner.merchant_account_state = Owner.BANK_ACCOUNT_PENDING
    return owner.save()


def update_account_state(merchant_account_id, state):
    owner = Owner.objects.get(merchant_id=merchant_account_id)
    owner.merchant_account_state = state
    owner.save()


def link_bank_account(owner, params):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    success, merchant_account_id, error_fields, error_msg = gateway.link_bank_account(params)
    if success:
        add_merchant_id_to_owner(merchant_account_id, owner)
        return [], []
    else:
        return error_fields, error_msg


def invite_legacy_owner(phone_number):
    '''
    Creates an auth.User for the given phone number, associates it whith an existing
    Owner object, and emails that User to reset their password, and link their bank account.

    Raises Owner.DoesNotExist if there wasn't an owner account for this number
    args:
    - phone_number: phone number of the user. Must contain no non-digit characters.
    '''
    created = False
    owner = Owner.objects.get(user_account__phone_number=phone_number)

    try:
        auth_user = User.objects.get(username=phone_number)
    except User.DoesNotExist:
        try:
            user_accounts = UserAccount.objects.filter(phone_number=phone_number, owner__isnull=False)
        except UserAccount.DoesNotExist:
            raise Owner.DoesNotExist
        user_account = user_accounts.latest('created_time')
        auth_user = auth_user_service.create_auth_user(user_account)


    if not auth_user in owner.auth_users.all():
        '''
        if they weren't already linked, scramble the password. This is just in case there was a
        driver account with the same phone number. We never validated their identity, so we can't
        just link the owner and this existing auth.User.
        '''
        password = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(8)])
        auth_user.set_password(password)
        auth_user.save()
        owner.auth_users.add(auth_user)
        created = True

    password_reset_service.invite_owner(auth_user)
    return created, auth_user
