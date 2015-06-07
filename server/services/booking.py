# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from idlecars import email

from server.services import user_account as user_account_service
from server.services import driver as driver_service
from server.models import Booking


# TODO - move this to CRM app
def notify_ops(driver, booking):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': 'guys',
            'TEXT': '{} created a new booking.'.format(driver.full_name()),
            'CTA_LABEL': 'Check it out',
            'CTA_URL': 'https://www.idlecars.com{}'.format(
                reverse('admin:server_booking_change', args=(booking.pk,))
            ),
        }
    }
    email.send_async(
        template_name='single_cta',
        subject='New Booking from {}'.format(driver.full_name()),
        merge_vars=merge_vars,
    )


def create_booking(user_account_data, car):
    '''
    Creates a new booking
    arguments
    - user_account_data: an OrderedDict of user data as returned from
    validated_data in a serializer.
    - car: an existing car object
    '''
    user_account = user_account_service.find_or_create(user_account_data)
    driver = driver_service.find_or_create(user_account)

    booking = Booking.objects.create(
        user_account=user_account, # TODO(JP): remove this deprecated field
        driver = driver,
        car = car,
    )
    if booking:
        notify_ops(driver, booking)

    return booking
