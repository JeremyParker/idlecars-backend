# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from . import Car, UserAccount, Driver
import datetime


class Booking(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True) # TODO(JP): remove deprecated field
    driver = models.ForeignKey(Driver, null=True) # TODO(JP): null=False after migration & backfill
    car = models.ForeignKey(Car, null=False)

    # these payemnt terms are only set after the driver puts down a deposit on the booking
    weekly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True
    )

    # time of day in end_time is estimated until pickup_time is set.
    end_time = models.DateTimeField(null=True, blank=True)  # end time set by the user

    #state transition times
    created_time = models.DateTimeField(auto_now_add=True)              # PENDING
    checkout_time = models.DateTimeField(null=True, blank=True)         # RESERVED <-- deprecated
    requested_time = models.DateTimeField(null=True, blank=True)        # REQUESTED
    approval_time = models.DateTimeField(null=True, blank=True)         # ACCEPTED
    pickup_time = models.DateTimeField(null=True, blank=True)           # ACTIVE <-- deprecated
    return_time = models.DateTimeField(null=True, blank=True)           # RETURNED <-- deprecated
    refund_time = models.DateTimeField(null=True, blank=True)           # REFUNDED
    incomplete_time = models.DateTimeField(null=True, blank=True)       # INCOMPLETE

    REASON_ANOTHER_BOOKED_DOCS = 1
    REASON_OWNER_REJECTED = 2
    REASON_DRIVER_REJECTED = 3
    REASON_MISSED = 4
    REASON_TEST_BOOKING = 5
    REASON_CANCELED = 6
    REASON_DRIVER_TOO_SLOW_DOCS = 7
    REASON_OWNER_TOO_SLOW = 8
    REASON_INSURANCE_REJECTED_AGE = 9
    REASON_INSURANCE_REJECTED_EXP = 10
    REASON_INSURANCE_REJECTED_PTS = 11
    REASON_BASE_LETTER = 12
    REASON_OTHER = 13
    REASON_ANOTHER_BOOKED_CC = 14
    REASON_DRIVER_TOO_SLOW_CC = 15

    REASON = (
        (REASON_ANOTHER_BOOKED_DOCS, 'Missed (Docs)'),
        (REASON_ANOTHER_BOOKED_CC, 'Missed (CC)'),
        (REASON_OWNER_REJECTED, 'Rejected by Owner'), # TODO - remove
        (REASON_DRIVER_REJECTED, 'Rejected by Driver'),
        (REASON_MISSED, 'Rented Elsewhere'),
        (REASON_TEST_BOOKING, 'Test'),
        (REASON_CANCELED, 'Driver Canceled'),
        (REASON_DRIVER_TOO_SLOW_DOCS, 'Timed out (Docs)'),
        (REASON_DRIVER_TOO_SLOW_CC, 'Timed out (CC)'),
        (REASON_OWNER_TOO_SLOW, 'Timed out Owner/Ins'),
        (REASON_INSURANCE_REJECTED_AGE, 'Insurance rejected: age'),
        (REASON_INSURANCE_REJECTED_EXP, 'Insurance rejected: exp'),
        (REASON_INSURANCE_REJECTED_PTS, 'Insurance rejected: pts'),
        (REASON_BASE_LETTER, 'No Base Letter'),
        (REASON_OTHER, 'Other'),
    )
    incomplete_reason = models.IntegerField(choices=REASON, null=True, blank=True)

    PENDING = 1
    REQUESTED = 3
    RETURNED = 6
    REFUNDED = 7
    INCOMPLETE = 8

    notes = models.TextField(blank=True)

    STATES = {
        PENDING: 'Pending - booking has been created but not reserved yet',
        REQUESTED: 'Requested - waiting for owner/insurance',
        RETURNED: 'Accepted - Owner has approved the driver to get on the car',
        REFUNDED: 'Finished - the owner requested that the driver be removed from the car',
        INCOMPLETE: 'Incomplete - this rental didn\'t happen for some reason (see reason field)',
    }

    def get_state(self):
        if self.incomplete_time:
            return Booking.INCOMPLETE
        elif self.refund_time:
            return Booking.REFUNDED
        elif self.approval_time:
            return Booking.RETURNED
        elif self.requested_time:
            return Booking.REQUESTED
        else:
            return Booking.PENDING

    def __unicode__(self):
        return '{} on {}'.format(self.driver, self.car)

    def clean(self, *args, **kwargs):
        '''
        Detect if someone is changing the state of the booking through the admin. If so, call
        the appropriate function to handle the state change.
        '''
        from server.services import booking as booking_service
        super(Booking, self).clean()
        if self.pk:
            orig = Booking.objects.get(pk=self.pk)
            if self.approval_time and not orig.approval_time:
                booking_service.on_insurance_approved(self)

            if self.incomplete_time:
                if not self.incomplete_reason:
                    raise ValidationError('To set a booking to incomplete, also select a reason')
                if not orig.incomplete_time:
                    booking_service.on_incomplete(self, orig.get_state())

        # check that all the date/times of events make sense
        max_time = timezone.make_aware(timezone.datetime.max, timezone.get_default_timezone())
        times = [
            self.requested_time or max_time,
            self.approval_time or max_time,
            self.refund_time or max_time,
        ]
        for earlier, later in zip(times[:-1], times[1:]):
            if earlier > later:
                raise ValidationError('The event times aren\'t in order')
