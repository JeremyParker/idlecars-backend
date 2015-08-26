# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse

import braintree

def _register_bt_endpoint(request):
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        'cg5tqqwr6fn5xycb',
        '7vyzyb772bwnhj3x',
        '951f45c0a8bf94e474b8eb5e956402fd'
    )
    reply = braintree.WebhookNotification.verify(request.GET['bt_challenge'])
    return HttpResponse(reply, content_type='text/plain')

def submerchant_create_success(request):
    if request.method == "GET":
        return _register_bt_endpoint(request)

def submerchant_create_failure(request):
    if request.method == "GET":
        return _register_bt_endpoint(request)
