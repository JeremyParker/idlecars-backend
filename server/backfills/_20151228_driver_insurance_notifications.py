# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone

from server.models import Booking
from server.services import booking as booking_service
from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the existing requested bookings which was created 47 hours ago FirstInsuranceNotification so that
    drivers don't get two reminders at the same time when we launch
    '''
    campaign = 'FirstInsuranceNotification'
    backfill_bookings = booking_service.filter_requested(Booking.objects.all()).filter(
        requested_time__lte=timezone.now() - datetime.timedelta(hours=47),
    )
    throttle_service.mark_sent(throttle_service.throttle(backfill_bookings, campaign), campaign)
