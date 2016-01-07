# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone

from server.models import Booking
from server.services import  booking as booking_service

from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the accepted bookings which was approved 1 hours ago
    FirstOwnerPickupReminder so that they don't get two reminders at the same
    time when we launch
    '''
    campaign = 'FirstOwnerPickupReminder'
    backfill_bookings = booking_service.filter_accepted(Booking.objects.all()).filter(
        approval_time__lte=timezone.now() - datetime.timedelta(hours=1),
    )
    print 'total backfill bookings: {}'.format(backfill_bookings.count())
    throttle_service.mark_sent(throttle_service.throttle(backfill_bookings, campaign), campaign)
