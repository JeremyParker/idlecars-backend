# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

import braintree

def add_merchant_id_to_owner(merchant_id, owner):
    owner.merchant_id = merchant_id
    return owner.save()

def link(owner, braintree_params):
    # TODO: @jeremyparker will move this when needed
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        'cg5tqqwr6fn5xycb',
        '7vyzyb772bwnhj3x',
        '951f45c0a8bf94e474b8eb5e956402fd'
    )

    braintree_params['funding']['destination'] = braintree.MerchantAccount.FundingDestination.Bank
    braintree_params['master_merchant_account_id'] = settings.MASTER_MERCHANT_ACCOUNT_ID

    result = braintree.MerchantAccount.create(braintree_params)
    if type(result) is braintree.successful_result.SuccessfulResult:
        add_merchant_id_to_owner(result.merchant_account.id, owner)
        return {}
    else:
        return {
            'error': result.message,
            '_app_notifications': [result.message]
        }
