# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from idlecars import email, client_side_routes


def documents_approved_no_booking(driver):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': driver.first_name(),
            'TEXT': 'Your uploaded documents have been reviewed and approved. You are now ready to rent any car on idlecars with one tap!',
            'CTA_LABEL': 'Rent a car now',
            'CTA_URL': client_side_routes.car_listing_url()
            ),
        }
    }
    email.send_async(
        template_name='single_cta',
        subject='Welcome to idlecars, {}'.format(booking.driver.full_name()),
        merge_vars=merge_vars,
    )
