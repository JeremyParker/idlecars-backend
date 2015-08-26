# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from server import payment_gateways
from server import models


def create_payment(booking, amount, payment_method):
    assert payment_method.driver == booking.driver
    payment = models.Payment.objects.create(
        booking=booking,
        amount=amount,
        payment_method=payment_method,
    )

    gateway_name = payment_method.gateway_name if payment_method else settings.PAYMENT_GATEWAY_NAME
    gateway = payment_gateways.get_gateway(gateway_name)

    result, transaction_id, error_message = gateway.make_payment(
        payment,
        token=payment_method.gateway_token
    )
    assert result in [
        models.Payment.APPROVED,
        models.Payment.DECLINED,
        models.Payment.REJECTED,
    ]
    payment.status = result
    payment.error_message = error_message
    payment.transaction_id = transaction_id
    payment.save()

    return payment
