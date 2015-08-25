# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree


def submerchant_create_success(request):
    if request.method == "GET":
        return braintree.WebhookNotification.verify(request.GET['bt_challenge'])

def submerchant_create_failure(request):
    print request
    if request.method == "GET":
        return braintree.WebhookNotification.verify(request.GET['bt_challenge'])
