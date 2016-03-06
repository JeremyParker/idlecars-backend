# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.conf import settings

from idlecars import email

from server import models

from owner_crm.models import notification


class DocumentsUploaded(notification.OpsNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': 'dudes',
            'HEADLINE': 'Driver Docs uploaded!',
            'TEXT': 'Someone with the number {} uploaded all thier docs. No action is required'.format(
                kwargs['driver_phone_number']
            ),
            'CTA_LABEL': 'Check \'em out',
            'CTA_URL': kwargs['driver_admin_link'],
            'template_name': 'one_button_no_image',
            'subject': 'Uploaded documents from {}'.format(kwargs['driver_phone_number']),
        }


class PaymentFailed(notification.OpsNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': 'peeps',
            'HEADLINE': 'A payment failed',
            'TEXT': 'the driver with phone {} had a payment fail for {}. The server response was:<br>{}'.format(
                kwargs['driver_phone_number'],
                kwargs['payment_invoice_description'],
                kwargs['payment_notes'],
            ),
            'CTA_LABEL': 'Payment details',
            'CTA_URL': kwargs['payment_admin_link'],
            'template_name': 'one_button_no_image',
            'subject': 'Payment {} for a {} ({}) failed.'.format(
                kwargs['payment'],
                kwargs['car_name'],
                kwargs['car_plate'],
            ),
        }


class PaymentJobFailed(notification.OpsNotification):
    def __init__(self, campaign_name, argument, *args):
        super(PaymentJobFailed, self).__init__(campaign_name, argument)
        self.message = args[0]

    def get_context(self, **kwargs):
        return {
            'FNAME': 'people',
            'HEADLINE': 'The payment job threw a {}'.format(self.message),
            'TEXT': 'the auto-payment job ran into a problem while processing payment for a booking.',
            'CTA_LABEL': 'Booking details',
            'CTA_URL': kwargs['booking_admin_link'],
            'template_name': 'one_button_no_image',
            'subject': 'The payment job failed.',
        }


class OwnerAccountDeclined(notification.OpsNotification):
    def __init__(self, campaign_name, argument, *args):
        super(OwnerAccountDeclined, self).__init__(campaign_name, argument)
        self.errors = args[0]

    def get_context(self, **kwargs):
        return {
            'FNAME': 'Dearest Admin',
            'HEADLINE': 'An owner\'s bank account was declined',
            'TEXT': '''
                {}'s bank account details were declined by the Braintree gateway.<br>
                Braintree returned the following error(s):<br>
                <ul>{}</ul>
            '''.format(kwargs['owner_name'], ''.join(['<li>{}'.format(e) for e in self.errors])),
            'template_name': 'no_button_no_image',
            'subject': '{}\'s bank account was declined'.format(kwargs['owner_name']),
        }


class NewUserMessage(notification.OpsNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': 'Ops team',
            'HEADLINE': 'A new message from user {}'.format(kwargs['message_first_name']),
            'TEXT': '''
                User first name is: {}
                <br />
                User email is: {}
                <br />
                Message is: <br /> {}
            '''.format(kwargs['message_first_name'], kwargs['message_email'], kwargs['message_body']),
            'template_name': 'no_button_no_image',
            'subject': 'A new message from user {}'.format(kwargs['message_first_name']),
        }
