# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from idlecars import email

from server.services import user_account as user_account_service
from server.services import driver as driver_service
from server.models import Booking


# TODO - move this to CRM app
def notify_ops(booking):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': 'guys',
            'TEXT': '{} created a new booking.'.format(booking.driver.full_name()),
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


def create_booking(car, driver):
    '''
    Creates a new booking
    arguments
    - car: an existing car object
    - driver: the driver making the booking
    '''
    booking = Booking.objects.create(
        driver=driver,
        car=car,
    )
    notify_ops(booking)
    return booking
