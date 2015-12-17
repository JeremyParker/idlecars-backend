# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.utils import crypto, timezone

from credit.models import CreditCode, Customer


class CreditError(Exception):
    pass


def _code_no_good(code_string):
    return len(code_string) < 4 or CreditCode.objects.filter(credit_code=code_string).exists()


def generate_invite_code_string(customer=None, code=''):
    if customer:
        name = customer.user.first_name or customer.user.last_name or customer.user.email
        code = name.upper()[:8]
        code = ''.join(x for x in code if x.isalpha())

    while _code_no_good(code):
        code = code + crypto.get_random_string(1, "34689") # so we don't create a word
        while _code_no_good(code):
            code = code + crypto.get_random_string(1, "ABCDEFGHJKLMNPQRTWXY34689")

    return code


def create_invite_code(invitee_amount, invitor_amount='0.00', customer=None):
    code_string = generate_invite_code_string(customer)

    description = ''
    if customer:
        description = '{} {}\'s invite code'.format(
            customer.user.first_name,
            customer.user.last_name,
        )

    invite_code = CreditCode.objects.create(
        credit_code=code_string,
        credit_amount=decimal.Decimal(invitee_amount),
        invitor_credit_amount=decimal.Decimal(invitor_amount),
        description=description,
        expiry_time=None,  # TODO: are we gonna do expiration?
    )
    if customer:
        customer.invite_code = invite_code
        customer.save()
    return invite_code


def redeem_code(code_string, customer):
    '''
    This function redeems a referral code and grants app credit to the user.
    WHOEVER CALLS THIS IS RESPONSIBILE FOR MAKING SURE IT'S A *NEW* USER!!!
    '''
    if code_string is None:
        raise CreditError('Sorry, we don\'t recognize this code.')

    try:
        code = CreditCode.objects.get(credit_code=code_string.upper())
    except CreditCode.DoesNotExist:
        raise CreditError('Sorry, we don\'t recognize this code.')

    if code.expiry_time is not None and code.expiry_time < timezone.now():
        raise CreditError('Sorry, this code has expired.')

    if customer.invitor_code:
        raise CreditError('It looks like you\'ve already used a referral code.')

    if customer.invite_code == code:
        raise CreditError('Woah pal! You can\'t use your own code.')

    code.redeem_count += 1
    code.save()
    customer.invitor_code = code
    customer.app_credit += code.credit_amount
    customer.save()


def is_reward_virgin(invitor_customer):
    '''
    Has this customer ever been rewarded for an invite code?
    '''
    return not Customer.objects.filter(
        invitor_code=invitor_customer.invite_code,
        invitor_credited=True
    )


def reward_invitor_for(new_customer):
    '''
    When a new customer converts, the customer who invited them is awarded app credit.
    '''
    if new_customer.invitor_code and not new_customer.invitor_credited:
        try:
            invitor = Customer.objects.get(invite_code=new_customer.invitor_code)
            invitor.app_credit += new_customer.invitor_code.invitor_credit_amount
            invitor.save()
        except Customer.DoesNotExist:
            # we may have issued the code ourselves, as a one-sided incentive code.
            pass
        new_customer.invitor_credited = True
        new_customer.save()
        return True, invitor
    return False, None
