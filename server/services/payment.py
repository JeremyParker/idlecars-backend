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
    create_payment's parameters are the way the outside world sees the payment. The way the payment
    is actually paid is reflected in the Payment object that is returned. Credit deductions are
    handled at this level. (Braintree and FakeGateway know nothing of credits)

    @booking - the booking that this payment applies to
    @cash_amount - how much cash the driver will actually pay
    @credit_amount - how much credit the driver will actually use up
    @service_fee - how much of the total value of the payment the owner will NOT get.
    @invoice_start_time - start of the period covered
    @invoice_end_time - end of the period covered
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

    cash_amount = Decimal(cash_amount)
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


def _deduct_app_credit(payment):
    if payment.credit_amount:
        customer = payment.booking.driver.auth_user.customer
        customer.app_credit -= payment.credit_amount
        customer.save()


def pre_authorize(payment):
    payment = _execute('pre_authorize', payment)
    if not payment.error_message:
        _deduct_app_credit(payment)
    return payment


def settle(payment):
    from server.services import driver as driver_service
    is_converted_driver = driver_service.is_converted_driver(payment.booking.driver)

    original_status = payment.status
    payment = _execute('settle', payment)

    if not payment.error_message:
        if not is_converted_driver:
            driver_service.on_newly_converted(payment.booking.driver)

        # if the payment succeeded, and credit wasn't already deducted, deduct now.
        if original_status != models.Payment.PRE_AUTHORIZED:
            _deduct_app_credit(payment)
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


def refund(payment):
    return _execute('refund', payment)


# TODO - this function and the one for payment_method should probably be moved to wherever the
# Braintree abstaction is.
def _braintree_link(transaction_id):
    l = '<a href="https://{base_url}/merchants/{account}/transactions/{token}">{token}</a>'.format(
        base_url=settings.BRAINTREE_BASE_URL,
        account=settings.BRAINTREE["merchant_id"],
        token=transaction_id,
    )
    return mark_safe(l)


def details_link(payment):
    return _braintree_link(payment.transaction_id)


def idlecars_supplement_link(payment):
    return _braintree_link(payment.idlecars_transaction_id)


def payment_method_link(payment_method):
    link =  '<a href="https://{base}/merchants/{account}/payment_methods/any/{t}">{t}</a>'.format(
        base=settings.BRAINTREE_BASE_URL,
        account=settings.BRAINTREE["merchant_id"],
        t=payment_method.gateway_token,
    )
    return mark_safe(link)
