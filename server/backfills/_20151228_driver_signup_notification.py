# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone

from server import models
from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the existing drivers who signed up 29 days ago FirstSignupReminder so that
    they don't get two reminders at the same time when we launch
    '''
    campaign = 'SignupFirstReminder'
    backfill_drivers = models.Driver.objects.filter(
        auth_user__date_joined__lte=timezone.now() - datetime.timedelta(days=29),
        braintree_customer_id__isnull=True,
    )
    backfill_drivers = throttle_service.throttle(backfill_drivers, campaign):
    skip_drivers = []
    from server.services import booking
    for driver in backfill_drivers:
        if booking.post_pending_bookings(driver.booking_set):
            skip_drivers.append(driver.pk)
            continue
        print '.'
    throttle_service.mark_sent(backfill_drivers.exclude(pk__in=skip_drivers), campaign)
