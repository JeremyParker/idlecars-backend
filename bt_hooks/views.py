# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404

from idlecars import email
from server import payment_gateways
from server.models import Owner
from server.services import owner_service
from owner_crm.services import ops_emails


def _confirm_bt_endpoint(request):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    reply = gateway.confirm_endpoint(request.GET['bt_challenge'])
    return HttpResponse(reply, content_type='text/plain')


def _get_webhook_notification(request):
    bt_signature = request.POST['bt_signature']
    bt_payload = request.POST['bt_payload']
    return braintree.WebhookNotification.parse(bt_signature, bt_payload)


def _handle_post(request, new_state):
    try:
        webhook_notification = _get_webhook_notification(request)
        owner_service.update_account_state(
            webhook_notification.merchant_account.id,
            new_state,
        )
        ops_emails.owner_account_result(str(request.POST), 'Owner Bank Account Processed')
        return HttpResponse('')
    except braintree.exceptions.InvalidSignatureError:
        # hide the error - somebody's trying to hack us?
        return HttpResponse('')
    except Owner.DoesNotExist:
        # TODO - some kind of email, or record of the failure.
        raise Http404


@csrf_exempt
def submerchant_create_success(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        return _handle_post(request, Owner.BANK_ACCOUNT_APPROVED)


@csrf_exempt
def submerchant_create_failure(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        return _handle_post(request, Owner.BANK_ACCOUNT_DECLINED)
