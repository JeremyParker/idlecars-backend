# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.conf import settings

from idlecars import email


def new_booking_email(booking):
    merge_vars = {
        settings.OPS_EMAIL: {
            'FNAME': 'guys',
            'HEADLINE': 'New Booking!',
            'TEXT': 'Driver {} booked {}\'s {}.'.format(
                booking.driver.phone_number(),
                booking.car.owner.name(),
                booking.car.__unicode__()),
            'CTA_LABEL': 'Check it out',
            'CTA_URL': 'https://www.idlecars.com{}'.format(
                reverse('admin:server_booking_change', args=(booking.pk,))
            ),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='New Booking from {}'.format(booking.driver.phone_number()),
        merge_vars=merge_vars,
    )

def documents_uploaded(driver):
    merge_vars = {
        settings.OPS_EMAIL: {
            'FNAME': 'dudes',
            'HEADLINE': 'Driver Docs uploaded!',
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
        template_name='one_button_no_image',
        subject='Uploaded documents from {}'.format(driver.phone_number()),
        merge_vars=merge_vars,
    )
