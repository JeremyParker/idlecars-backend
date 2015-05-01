# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.services import user_account as user_account_service
from server.models import Booking


def create_booking(user_account_data, car):
    '''
    Creates a new booking
    arguments
    - user_account_data: an OrderedDict of user data as returned from
    validated_data in a serializer.
    - car: an existing car object
    '''
    user_account = user_account_service.find_or_create(user_account_data)

    return Booking.objects.create(
        user_account = user_account,
        car = car,
    )
