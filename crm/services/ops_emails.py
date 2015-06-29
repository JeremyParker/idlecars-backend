# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from idlecars import email


def new_booking_email(booking):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': 'guys',
            'TEXT': 'Someone with the number {} created a new booking.'.format(booking.driver.phone_number()),
            'CTA_LABEL': 'Check it out',
            'CTA_URL': 'https://www.idlecars.com{}'.format(
                reverse('admin:server_booking_change', args=(booking.pk,))
            ),
        }
    }
    email.send_async(
        template_name='single_cta',
        subject='New Booking from {}'.format(booking.driver.phone_number()),
        merge_vars=merge_vars,
    )

def documents_uploaded(driver):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': 'dudes',
            'TEXT': 'Someone with the number {} uploaded all thier docs. Please see if they\'re legit'.format(
                driver.phone_number()
            ),
            'CTA_LABEL': 'Check \'em out',
            'CTA_URL': 'https://www.idlecars.com{}'.format(
                reverse('admin:server_driver_change', args=(driver.pk,))
            ),
        }
    }
    email.send_async(
        template_name='single_cta',
        subject='Uploaded documents from {}'.format(driver.phone_number()),
        merge_vars=merge_vars,
    )
