# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


def create_payment(booking, amount, credit_card=None, nonce=None):
    assert credit_card or nonce

    payment = models.Payment.objects.create(booking=booking, amount=amount)
    if credit_card:
        assert credit_card.customer == booking.driver.auth_user
        payment.credit_card = credit_card

    gateway_name = credit_card.gateway_name if credit_card else settings.PAYMENT_GATEWAY_NAME
    gateway = payment_gateways.get_gateway(gateway_name)

    result, token, error_message, expiry_date = gateway.make_payment(payment, nonce)

    assert result in [
        models.Payment.APPROVED,
        models.Payment.DECLINED,
        models.Payment.REJECTED,
    ]
    payment.status = result
    payment.error_message = error_message
    payment.gateway_token = token
    payment.save()

    # save the expiration date in case we didn't have it before
    # if credit_card and expiry_date and expiry_date != credit_card.expiry_date:
    #     credit_card.expiry_date = expiry_date
    #     credit_card.save(update_fields=('expiry_date',))

    return payment
