# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.utils import crypto, timezone
from django.conf import settings

from credit.models import CreditCode


def generate_invite_code_string(customer):
    name = customer.user.first_name or customer.user.last_name or customer.user.email
    code = name.upper()[:8]
    while CreditCode.objects.filter(credit_code=code).exists():
        code = code + crypto.get_random_string(1, "34689") # so we don't create a word
        while CreditCode.objects.filter(credit_code=code).exists():
            code = code + crypto.get_random_string(1, "ABCDEFGHJKLMNPQRTWXY34689")
    return code


def create_invite_code(customer):
    # TODO - customers are randomly assigned to a cohort (50/50 or 25/75)
    code = generate_invite_code_string(customer)
    invite_code = CreditCode.objects.create(
        credit_code=code,
        credit_amount=decimal.Decimal(settings.SIGNUP_CREDIT),
        invitor_credit_amount=decimal.Decimal(settings.INVITOR_CREDIT),
        expiry_time=None,
    )
    return invite_code


def redeem_code(code_string, customer):
    '''
    This function redeems a referral code and grants app credit to the user.
    WHOEVER CALLS THIS IS RESPONSIBILE FOR MAKING SURE IT'S A *NEW* USER!!!
    '''
    if credit_code is None:
        return

    try:
        code = CreditCode.objects.get(credit_code=code_string.upper())
    except CreditCode.DoesNotExist:
        raise Exception("Sorry, we don\'t recognize this code.")

    if code.expiry_time is not None and code.expiry_time < timezone.now():
        raise Exception("Sorry, this code has expired.")

    if customer.invitor_code:
        raise Exception("It looks like you\'ve already used an invitation code.")

    if customer.invite_code == code:
        raise Exception("Sorry pal, you can't use your own code.")

    code.redeem_count += 1
    code.save()
    customer.invitor_code = code
    customer.app_credit += code.credit_amount
    customer.save()
