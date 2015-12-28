# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models, services

def run_backfill():
    '''
    mark throttle system the existing drivers who signed up 29 days ago FirstSignupReminder so that
    they don't get two reminders at the same time when we launch
    '''

    backfill_drivers = models.Driver.objects.filter(
        auth_user__date_joined__lte=timezone.now() - datetime.timedelta(days=29),
        braintree_customer_id__isnull=True,
    )
    skip_drivers = []
    for driver in backfill_drivers:
        if services.booking.post_pending_bookings(driver.booking_set):
            skip_drivers.append(driver.pk)
            continue
    throttle_service.mark_sent(backfill_drivers.exclude(pk__in=skip_drivers), 'SignupFirstReminder')
