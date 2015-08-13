# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from . import Car, UserAccount, Driver
import datetime


class Booking(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True) # TODO(JP): remove deprecated field
    driver = models.ForeignKey(Driver, null=True) # TODO(JP): null=False after migration & backfill
    car = models.ForeignKey(Car, null=False)

    end_time = models.DateTimeField(null=True)  # end time set by the user

    #state transition times
    created_time = models.DateTimeField(auto_now_add=True)  # PENDING
    checkout_time = models.DateTimeField(null=True)         # still PENDING
    requested_time = models.DateTimeField(null=True)        # REQUESTED
    approval_time = models.DateTimeField(null=True)         # ACCEPTED
    pickup_time = models.DateTimeField(null=True)           # BOOKED
    return_time = models.DateTimeField(null=True)           # (new state)
    incomplete_time = models.DateTimeField(null=True)       # CANCELED
    refund_time = models.DateTimeField(null=True)           # (new state)

    REASON_TOO_SLOW = 1
    REASON_OWNER_REJECTED = 2
    REASON_DRIVER_REJECTED = 3
    REASON_MISSED = 4
    REASON_TEST_BOOKING = 5
    REASON_CANCELED = 6
    REASON = (
        (REASON_TOO_SLOW, 'Too Slow - somebody else booked your car'),
        (REASON_OWNER_REJECTED, 'Owner Rejected - driver wasn\t approved'),
        (REASON_DRIVER_REJECTED, 'Driver Rejected - driver changed their mind'),
        (REASON_MISSED, 'Missed - car rented out before we found a driver'),
        (REASON_TEST_BOOKING, 'Test - a booking that one of us created as a test'),
        (REASON_CANCELED, 'Canceled - driver canceled the booking thru the app'),
    )
    incomplete_reason = models.IntegerField(choices=REASON, null=True)


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

    STATE = (
        (PENDING, 'Pending - waiting for driver docs'),
        (COMPLETE, 'Complete - checking driver creds'),
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
    state = models.IntegerField(choices=STATE, default=PENDING)
    notes = models.TextField(blank=True)
