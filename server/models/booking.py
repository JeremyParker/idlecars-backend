# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from . import Car, UserAccount, Driver
import datetime


class Booking(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True) # TODO(JP): remove deprecated field
    driver = models.ForeignKey(Driver, null=True) # TODO(JP): null=False after migration & backfill
    car = models.ForeignKey(Car, null=False)

    end_time = models.DateTimeField(null=True, blank=True)  # end time set by the user

    #state transition times
    created_time = models.DateTimeField(auto_now_add=True)              # PENDING
    checkout_time = models.DateTimeField(null=True, blank=True)         # RESERVED
    requested_time = models.DateTimeField(null=True, blank=True)        # REQUESTED
    approval_time = models.DateTimeField(null=True, blank=True)         # ACCEPTED
    pickup_time = models.DateTimeField(null=True, blank=True)           # BOOKED
    return_time = models.DateTimeField(null=True, blank=True)           # RETURNED
    refund_time = models.DateTimeField(null=True, blank=True)           # REFUNDED
    incomplete_time = models.DateTimeField(null=True, blank=True)       # INCOMPLETE

    REASON_ANOTHER_BOOKED = 1
    REASON_OWNER_REJECTED = 2
    REASON_DRIVER_REJECTED = 3
    REASON_MISSED = 4
    REASON_TEST_BOOKING = 5
    REASON_CANCELED = 6
    REASON = (
        (REASON_ANOTHER_BOOKED, 'Too Slow - another driver on our system booked the car'),
        (REASON_OWNER_REJECTED, 'Owner Rejected - driver wasn\t approved'),
        (REASON_DRIVER_REJECTED, 'Driver Rejected - driver changed their mind'),
        (REASON_MISSED, 'Missed - car rented out elsewhere before we found a driver'),
        (REASON_TEST_BOOKING, 'Test - a booking that one of us created as a test'),
        (REASON_CANCELED, 'Canceled - driver canceled the booking thru the app'),
    )
    incomplete_reason = models.IntegerField(choices=REASON, null=True, blank=True)

    STATE_FROM_EVENT_TIMES = 0
    PENDING = 1
    COMPLETE = 2
    REQUESTED = 3
    ACCEPTED = 4
    BOOKED = 5
    FLAKE = 6
    TOO_SLOW = 7
    OWNER_REJECTED = 8
    DRIVER_REJECTED = 9
    MISSED = 10
    TEST_BOOKING = 11
    CANCELED = 12
    RESERVED = 13    # deposit paid, but not requested on insurance yet (waiting for doc review)
    RETURNED = 14    # returned to owner, but not refunded the deposit yet
    REFUNDED = 15    # returned and refunded
    INCOMPLETE = 16  # canceled or someone else booked, ...etc. and refunded if necessary

    OLD_STATES = (
        (STATE_FROM_EVENT_TIMES, 'State comes from event times, not from this field.'),
        (PENDING, 'Pending - waiting for driver docs'),
        (COMPLETE, 'Deprecated'),
        (REQUESTED, 'Requested - waiting for owner/insurance'),
        (ACCEPTED, 'Accepted - waiting for deposit, ssn, contract'),
        (BOOKED, 'Booked - car marked busy with new available_time'),
        (FLAKE, 'Flake - Didn\'t Submit Docs in 24 hours'),
        (TOO_SLOW, 'Too Slow - somebody else booked your car'),
        (OWNER_REJECTED, 'Owner Rejected - driver wasn\t approved'),
        (DRIVER_REJECTED, 'Driver Rejected - driver changed their mind'),
        (MISSED, 'Missed - car rented out before we found a driver'),
        (TEST_BOOKING, 'Test - a booking that one of us created as a test'),
        (CANCELED, 'Canceled - driver canceled the booking thru the app'),
    )
    state = models.IntegerField(choices=OLD_STATES, default=STATE_FROM_EVENT_TIMES)
    notes = models.TextField(blank=True)

    STATES = {
        PENDING: 'Pending - booking has been created but not reserved yet',
        RESERVED: 'Reserved - deposit paid, not requested (waiting for doc review)',
        REQUESTED: 'Requested - waiting for owner/insurance',
        ACCEPTED: 'Accepted - waiting for deposit, ssn, contract',
        BOOKED: 'Booked - car marked busy with new available_time',
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
            return Booking.BOOKED
        elif self.approval_time:
            return Booking.ACCEPTED
        elif self.requested_time:
            return Booking.REQUESTED
        elif self.checkout_time:
            return Booking.RESERVED
        else:
            return Booking.PENDING
