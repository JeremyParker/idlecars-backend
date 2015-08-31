# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree

from django.conf import settings

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
    success, merchant_account_id = gateway.link_bank_account(params)
    if success:
        add_merchant_id_to_owner(merchant_account_id, owner)
        return {}
    else:
        return {
            'error': response.message,
            '_app_notifications': [response.message]
        }


def invite_legacy_owner(phone_number):
    '''
    Creates an auth.User for the given phone number, associates it whith an existing
    Owner object, and emails that User to reset their password, and link their bank account.

    Raises either Owner.DoesNotExist or UserAccount.DoesNotExist
    args:
    - phone_number: phone number of the user. Must contain no non-digit characters.
    '''
    user_accounts = UserAccount.objects.filter(phone_number=phone_number, owner__isnull=False)
    if not user_accounts:
        raise UserAccount.DoesNotExist
    # we can only have one auth.User per phone. Use the most recent.
    user_account = user_accounts.latest('created_time')

    auth_user = auth_user_service.get_or_create_auth_user(user_account)
    if not auth_user in user_account.owner.auth_users.all():
        user_account.owner.auth_users.add(auth_user)

    password_reset_service.invite_owner(auth_user)
    return auth_user
