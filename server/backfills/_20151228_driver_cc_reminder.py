# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone

from server.models import Booking
from server.services import booking as booking_service
from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the existing bookings which was created 47 hours ago FirstSignupReminder so that
    drivers don't get two reminders at the same time when we launch
    '''

    filtered_bookings = Booking.objects.filter(
        created_time__lte=timezone.now() - datetime.timedelta(hours=47),
        driver__paymentmethod__isnull=True,
    )
    backfill_bookings = booking_service.filter_pending(filtered_bookings)
    for booking in backfill_bookings:
        print '.'
    throttle_service.mark_sent(backfill_bookings, 'FirstCCReminder')
