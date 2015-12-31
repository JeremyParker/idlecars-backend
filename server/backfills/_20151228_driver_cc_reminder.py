# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone
from django.db.models import Q

from server.models import Booking
from server.services import booking as booking_service
from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the existing bookings which was created 47 hours ago FirstSignupReminder so that
    drivers don't get two reminders at the same time when we launch
    '''
    campaign = 'FirstCCReminder'
    filtered_bookings = Booking.objects.filter(
        created_time__lte=timezone.now() - datetime.timedelta(hours=47),
    ).exclude(
        Q(driver__driver_license_image__exact='') |
        Q(driver__fhv_license_image__exact='') |
        Q(driver__address_proof_image__exact='') |
        Q(driver__defensive_cert_image__exact='')
    )
    backfill_bookings = booking_service.filter_pending(filtered_bookings)
    throttle_service.mark_sent(throttle_service.throttle(backfill_bookings, campaign), campaign)
