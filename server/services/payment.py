# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.conf import settings
from django.utils.safestring import mark_safe

from owner_crm.services import notification
from server import payment_gateways
from server import models


NO_PAYMENT_METHOD = 'Sorry, we don\'t have your payment method on file. Please add a credit card from your "My Account" page.'

def create_payment(
    booking,
    cash_amount,
    credit_amount='0.00',
    service_fee='0.00',
    invoice_start_time=None,
    invoice_end_time=None
):
    '''
    create_payment's parameters are the way the outside world sees the payment. The way the payment is
    actually paid is reflected in the Payment object.
    `service_fee` serves as a way of determining how much the owner should get.
    '''
    from server.services import driver as driver_service
    payment_method = driver_service.get_default_payment_method(booking.driver)
    if not payment_method:
        return models.Payment(
            booking=booking,
            error_message=NO_PAYMENT_METHOD,
            amount=cash_amount,
            credit_amount=credit_amount,
            status=models.Payment.REJECTED,
        )

    assert payment_method.driver == booking.driver
    credit_amount = Decimal(credit_amount)
    service_fee = Decimal(service_fee)
    supplement = Decimal('0.00')

    real_service_fee = service_fee - credit_amount
    if real_service_fee < Decimal('0.00'):
        supplement = -real_service_fee
        real_service_fee = Decimal('0.00')

    payment = models.Payment.objects.create(
        booking=booking,
        amount=cash_amount,
        credit_amount=credit_amount,
        idlecars_supplement=supplement,
        service_fee=real_service_fee,
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
        notification.send('ops_notifications.PaymentFailed', payment)
    return payment


def pre_authorize(payment):
    payment = _execute('pre_authorize', payment)
    if not payment.error_message:
        customer = payment.booking.driver.auth_user.customer
        customer.app_credit -= payment.credit_amount
        customer.save()
    return payment


def settle(payment):
    payment = _execute('settle', payment)
    # if not payment.error_message and payment.idlecars_supplement:
    #     supplement_payment = models.Payment.objects.create(
    #         booking=booking,
    #         amount=payment.idlecars_supplement,
    #         payment_method=idlecars_payment_method,
    #         invoice_start_time=payment.invoice_start_time,
    #         invoice_end_time=payment.invoice_end_time,
    #     )
    return payment


def void(payment):
    payment = _execute('void', payment)
    if not payment.error_message:
        customer = payment.booking.driver.auth_user.customer
        customer.app_credit += payment.credit_amount
        customer.save()
    return payment


def escrow(payment):
    return _execute('escrow', payment)


# TODO - this function and the one for payment_method should probably be moved to wherever the
# Braintree abstaction is.
def details_link(payment):
    l = '<a href="https://{base_url}/merchants/{account}/transactions/{token}">{token}</a>'.format(
        base_url=settings.BRAINTREE_BASE_URL,
        account=settings.BRAINTREE["merchant_id"],
        token=payment.transaction_id,
    )
    return mark_safe(l)


def payment_method_link(payment_method):
    link =  '<a href="https://{base}/merchants/{account}/payment_methods/any/{t}">{t}</a>'.format(
        base=settings.BRAINTREE_BASE_URL,
        account=settings.BRAINTREE["merchant_id"],
        t=payment_method.gateway_token,
    )
    return mark_safe(link)
