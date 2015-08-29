# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree

from django.conf import settings

from owner_crm.services import password_reset_service

from server.models import Owner, UserAccount
from server.services import auth_user as auth_user_service



def add_merchant_id_to_owner(merchant_id, owner):
    owner.merchant_id = merchant_id
    return owner.save()


def link_bank_account(owner, braintree_params):
    # TODO: @jeremyparker will move this when needed
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        'cg5tqqwr6fn5xycb',
        '7vyzyb772bwnhj3x',
        '951f45c0a8bf94e474b8eb5e956402fd'
    )

    braintree_params['funding']['destination'] = braintree.MerchantAccount.FundingDestination.Bank
    braintree_params['master_merchant_account_id'] = settings.MASTER_MERCHANT_ACCOUNT_ID

    response = braintree.MerchantAccount.create(braintree_params)
    success = getattr(response, "is_success", False)
    if success:
        add_merchant_id_to_owner(response.merchant_account.id, owner)
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

    auth_user = auth_user_service.create_auth_user(user_account)
    user_account.owner.auth_users.add(auth_user)

    password_reset_service.invite_owner(auth_user)
    return auth_user
