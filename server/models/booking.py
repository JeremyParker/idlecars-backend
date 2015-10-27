# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

from . import Car, UserAccount, Driver
import datetime


class Booking(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True) # TODO(JP): remove deprecated field
    driver = models.ForeignKey(Driver, null=True) # TODO(JP): null=False after migration & backfill
    car = models.ForeignKey(Car, null=False)

    # these payemnt terms are only set after the driver puts down a deposit on the booking
    weekly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    service_percentage = models.DecimalField(max_digits=10, decimal_places=4, null=True) # our take rate

    # time of day in end_time is estimated until pickup_time is set.
    end_time = models.DateTimeField(null=True, blank=True)  # end time set by the user

    #state transition times
    created_time = models.DateTimeField(auto_now_add=True)              # PENDING
    checkout_time = models.DateTimeField(null=True, blank=True)         # RESERVED
    requested_time = models.DateTimeField(null=True, blank=True)        # REQUESTED
    approval_time = models.DateTimeField(null=True, blank=True)         # ACCEPTED
    pickup_time = models.DateTimeField(null=True, blank=True)           # ACTIVE
    return_time = models.DateTimeField(null=True, blank=True)           # RETURNED
    refund_time = models.DateTimeField(null=True, blank=True)           # REFUNDED
    incomplete_time = models.DateTimeField(null=True, blank=True)       # INCOMPLETE

    REASON_ANOTHER_BOOKED = 1
    REASON_OWNER_REJECTED = 2
    REASON_DRIVER_REJECTED = 3
    REASON_MISSED = 4
    REASON_TEST_BOOKING = 5
    REASON_CANCELED = 6
    REASON_DRIVER_TOO_SLOW = 7
    REASON_OWNER_TOO_SLOW = 8
    REASON_INSURANCE_REJECTED_AGE = 9
    REASON_INSURANCE_REJECTED_EXP = 10
    REASON_INSURANCE_REJECTED_PTS = 11
    REASON_BASE_LETTER = 12
    REASON_OTHER = 13

    REASON = (
        (REASON_ANOTHER_BOOKED, 'Too Slow - another driver on our system booked the car'),
        (REASON_OWNER_REJECTED, 'The Owner Rejected - driver wasn\'t approved. Don\'t know why yet.'),
        (REASON_DRIVER_REJECTED, 'The Driver Rejected - at pickup'),
        (REASON_MISSED, 'Missed - car rented out elsewhere before we found a driver'),
        (REASON_TEST_BOOKING, 'Test - a booking that one of us created as a test'),
        (REASON_CANCELED, 'Canceled - driver canceled thru the app before insurance approval'),
        (REASON_DRIVER_TOO_SLOW, 'Driver Too Slow - driver did not submit their documents in time'),
        (REASON_OWNER_TOO_SLOW, 'Owner Too Slow - the insurance took too long'),
        (REASON_INSURANCE_REJECTED_AGE, 'Driver rejected from insurance - too young'),
        (REASON_INSURANCE_REJECTED_EXP, 'Driver rejected from insurance - experience'),
        (REASON_INSURANCE_REJECTED_PTS, 'Driver rejected from insurance - points'),
        (REASON_BASE_LETTER, 'No Base Letter - we cannot get a base letter'),
        (REASON_OTHER, 'Some other reason - see notes field below'),
    )
    incomplete_reason = models.IntegerField(choices=REASON, null=True, blank=True)

    STATE_UNKNOWN = 0
    PENDING = 1
    RESERVED = 2
    REQUESTED = 3
    ACCEPTED = 4
    ACTIVE = 5
    RETURNED = 6
    REFUNDED = 7
    INCOMPLETE = 8

    notes = models.TextField(blank=True)

    STATES = {
        PENDING: 'Pending - booking has been created but not reserved yet',
        RESERVED: 'Reserved - deposit paid, not requested (waiting for doc review)',
        REQUESTED: 'Requested - waiting for owner/insurance',
        ACCEPTED: 'Accepted - waiting for driver to pick up the car',
        ACTIVE: 'Active - car is in the driver\'s possession and on the road',
        RETURNED: 'Returned - driver returned the car but hasn\'t got deposit back',
        REFUNDED: 'Refunded - car was returned and driver got their deposit back',
        INCOMPLETE: 'Incomplete - this rental didn\'t happen for some reason (see reason field)',
    }

    def get_state(self):
        if self.incomplete_time:
            return Booking.INCOMPLETE
        elif self.refund_time:
            return Booking.REFUNDED
        elif self.return_time:
            return Booking.RETURNED
        elif self.pickup_time:
            return Booking.ACTIVE
        elif self.approval_time:
            return Booking.ACCEPTED
        elif self.requested_time:
            return Booking.REQUESTED
        elif self.checkout_time:
            return Booking.RESERVED
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

            if self.return_time and not orig.return_time:
                booking_service.on_returned(self)

            if self.incomplete_time:
                if not self.incomplete_reason:
                    raise ValidationError('To set a booking to incomplete, also select a reason')
                if not orig.incomplete_time:
                    booking_service.on_incomplete(self, orig.get_state())

    OLD_STATES = (
        (0, 'State comes from event times, not from this field.'),
        (1, 'Pending - waiting for driver docs'),
        (2, 'Complete - driver uploaded all docs'),
        (3, 'Requested - waiting for owner/insurance'),
        (4, 'Accepted - waiting for deposit, ssn, contract'),
        (5, 'Booked - car marked busy with new available_time'),
        (6, 'Flake - Didn\'t Submit Docs in 24 hours'),
        (7, 'Too Slow - somebody else booked your car'),
        (8, 'Owner Rejected - driver wasn\t approved'),
        (9, 'Driver Rejected - driver changed their mind'),
        (10, 'Missed - car rented out before we found a driver'),
        (11, 'Test - a booking that one of us created as a test'),
        (12, 'Canceled - driver canceled the booking thru the app'),
    )
    deprecated_state = models.IntegerField(choices=OLD_STATES, default=0)
