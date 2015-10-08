# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.utils.safestring import mark_safe

from owner_crm.services import ops_emails
from server import payment_gateways
from server import models


NO_PAYMENT_METHOD = 'Sorry, we don\'t have your payment method on file. Please add a credit card from your "My Account" page.'

def create_payment(
    booking,
    amount,
    service_fee='0.00',
    invoice_start_time=None,
    invoice_end_time=None
):
    if booking.driver:
        payment_method = booking.driver.paymentmethod_set.last() # TODO: store 'em all & make latest default
    if not payment_method:
        return models.Payment(
            booking=booking,
            error_message=NO_PAYMENT_METHOD,
            amount=amount,
            status=models.Payment.REJECTED,
        )

    assert payment_method.driver == booking.driver
    payment = models.Payment.objects.create(
        booking=booking,
        amount=amount,
        service_fee=service_fee,
        payment_method=payment_method,
        invoice_start_time=invoice_start_time,
        invoice_end_time=invoice_end_time,
    )
    return payment


def _execute(function, payment):
    '''
    Execute a payment gatway method on the active gateway. This accomplishes redirection
    between Braintree or Fake (or another gateway we might switch to in the future.)
    '''
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    func = getattr(gateway, function)
    payment = func(payment)
    payment.save()
    if payment.error_message:
        ops_emails.payment_failed(payment)
    return payment


def pre_authorize(payment):
    return _execute('pre_authorize', payment)


def settle(payment):
    return _execute('settle', payment)


def void(payment):
    return _execute('void', payment)


def escrow(payment):
    return _execute('escrow', payment)


def details_link(payment):
    link = '<a href="https://{base_url}/merchants/{account}/transactions/{token}">{token}</a>'.format(
        base_url=settings.BRAINTREE_BASE_URL,
        account=settings.BRAINTREE["merchant_id"],
        token=payment.transaction_id,
    )
    return mark_safe(link)
