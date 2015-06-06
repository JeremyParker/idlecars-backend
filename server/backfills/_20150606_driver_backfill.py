# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models

def run_backfill():
    '''
    associate a (new) driver object for all bookings
    '''
    for booking in models.Booking.objects.all():
        if models.Driver.objects.filter(user_account=booking.user_account).exists():
            booking.driver = models.Driver.objects.get(user_account=booking.user_account)
        else:
            booking.driver = models.Driver.objects.create(user_account = booking.user_account)
        print('.')
        booking.save()
