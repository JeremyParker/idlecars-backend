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

def _send_email_to_admin(request):
    merge_vars = {
        'jeff@idlecars.com': {
            'FNAME': 'Admin',
            'HEADLINE': 'Owner Bank Link Update',
            'TEXT': request.POST.__unicode__(),
            'CTA_LABEL': 'Dont click me',
            'CTA_URL': 'https://idlecars.com',
        }
    }
    email.send_sync(
        template_name='one_button_no_image',
        subject='Owner Bank Link Update',
        merge_vars=merge_vars,
    )


def submerchant_create_success(request):
    if request.method == 'GET':
        return _register_bt_endpoint(request)
    elif request.method == 'POST':
        _send_email_to_admin(request)
        return HttpResponse('')

def submerchant_create_failure(request):
    if request.method == 'GET':
        return _register_bt_endpoint(request)
    elif request.method == 'POST':
        _send_email_to_admin(request)
        return HttpResponse('')
