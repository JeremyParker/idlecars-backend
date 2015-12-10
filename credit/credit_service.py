# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.utils import crypto, timezone

from credit.models import CreditCode, Customer


class CreditException(Exception):
    pass


def generate_invite_code_string(customer=None, code=''):
    if customer:
        name = customer.user.first_name or customer.user.last_name or customer.user.email
        code = name.upper()[:8]
    while len(code) < 4 or CreditCode.objects.filter(credit_code=code).exists():
        code = code + crypto.get_random_string(1, "34689") # so we don't create a word
        while CreditCode.objects.filter(credit_code=code).exists():
            code = code + crypto.get_random_string(1, "ABCDEFGHJKLMNPQRTWXY34689")
    return code


def create_invite_code(invitee_amount, invitor_amount='0.00', customer=None):
    # TODO - customers are randomly assigned to a cohort (50/50 or 25/75)
    code_string = generate_invite_code_string(customer)
    invite_code = CreditCode.objects.create(
        credit_code=code_string,
        credit_amount=decimal.Decimal(invitee_amount),
        invitor_credit_amount=decimal.Decimal(invitor_amount),
        expiry_time=None,  # TODO: are we gonna do expiration?
    )
    if customer:
        invite_code.description = 'Invite code for {} {}'.format(
            customer.user.first_name,
            customer.user.last_name,
        )
        customer.invite_code = invite_code
        customer.save()
    return invite_code


def redeem_code(code_string, customer):
    '''
    This function redeems a referral code and grants app credit to the user.
    WHOEVER CALLS THIS IS RESPONSIBILE FOR MAKING SURE IT'S A *NEW* USER!!!
    '''
    if code_string is None:
        return

    try:
        code = CreditCode.objects.get(credit_code=code_string.upper())
    except CreditCode.DoesNotExist:
        raise CreditException("Sorry, we don\'t recognize this code.")

    if code.expiry_time is not None and code.expiry_time < timezone.now():
        raise CreditException("Sorry, this code has expired.")

    if customer.invitor_code:
        raise CreditException("It looks like you\'ve already used an invitation code.")

    if customer.invite_code == code:
        raise CreditException("Sorry pal, you can't use your own code.")

    code.redeem_count += 1
    code.save()
    customer.invitor_code = code
    customer.app_credit += code.credit_amount
    customer.save()


def on_cash_spent(new_customer):
    '''
    When a new customer spends cash, the referrer is awarded app credit.
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

