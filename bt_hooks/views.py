# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import braintree

from idlecars import email
from server import payment_gateways
from owner_crm.services import ops_emails


def _confirm_bt_endpoint(request):
    gateway = payment_gateways.get_gateway(settings.PAYMENT_GATEWAY_NAME)
    reply = gateway.confirm_endpoint(request.GET['bt_challenge'])
    return HttpResponse(reply, content_type='text/plain')


# TODO: confirm the request actually came from braintree
@csrf_exempt
def submerchant_create_success(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        ops_emails.owner_account_result(str(request.POST), 'Owner Bank Account Added')
        return HttpResponse('')

# TODO: confirm the request actually came from braintree
@csrf_exempt
def submerchant_create_failure(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        ops_emails.owner_account_result(str(request.POST), 'Owner Bank Account Rejected')
        return HttpResponse('')
