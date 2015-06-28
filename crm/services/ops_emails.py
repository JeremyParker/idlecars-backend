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
        subject='New Booking from {}'.format(booking.driver.full_name()),
        merge_vars=merge_vars,
    )
