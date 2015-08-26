# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import braintree

from idlecars import email


def _confirm_bt_endpoint(request):
    # TODO: @jeremeyparker will update this when config is moved to a general place
    braintree.Configuration.configure(
        braintree.Environment.Sandbox,
        'cg5tqqwr6fn5xycb',
        '7vyzyb772bwnhj3x',
        '951f45c0a8bf94e474b8eb5e956402fd'
    )
    reply = braintree.WebhookNotification.verify(request.GET['bt_challenge'])
    return HttpResponse(reply, content_type='text/plain')

def _send_email_to_admin(request, subject):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': 'Dearest Admin',
            'HEADLINE': subject,
            'TEXT': 'detail from braintree (if any):\n' + str(request.POST),
            'CTA_LABEL': 'button',
            'CTA_URL': 'https://idlecars.com',
        }
    }
    email.send_sync(
        template_name='one_button_no_image',
        subject=subject,
        merge_vars=merge_vars,
    )


@csrf_exempt
def submerchant_create_success(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        _send_email_to_admin(request, 'Owner Bank Account Added')
        return HttpResponse('')

@csrf_exempt
def submerchant_create_failure(request):
    if request.method == 'GET':
        return _confirm_bt_endpoint(request)
    elif request.method == 'POST':
        _send_email_to_admin(request, 'Owner Bank Account Rejected')
        return HttpResponse('')
