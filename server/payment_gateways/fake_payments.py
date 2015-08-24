# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from server import models


next_payment_response = None
add_card_log = []
make_payment_log = []

def add_card(desc, customer, device):
    global next_card_response
    add_card_log.append((
        customer,
        desc.number,
        desc.expiry_date,
        desc.cvv,
        desc.cardholder,
        desc.postcode,
        desc.country_code,
        device,
    ))

    if next_card_response is None:
        res = True, ("fake-token", "1234", "Visa", None, datetime.date(2012, 6, 1), "")
    else:
        res = next_card_response
        next_card_response = None
    return res

def make_payment(payment, nonce=None):
    global next_payment_response
    make_payment_log.append(payment)

    if next_payment_response:
        res = next_payment_response
    elif nonce:
        res = (models.Payment.APPROVED, "test", "", datetime.date(2015, 8, 30))
    else:
        res = (models.Payment.DECLINED, "test", "No funds available", datetime.date(2015, 8, 30))
    next_payment_response = None
    return res


def reset():
    global make_payment_log
    make_payment_log = []
