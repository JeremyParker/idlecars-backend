# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from . import Car, UserAccount, Driver


class Booking(models.Model):
    user_account = models.ForeignKey(UserAccount, null=True) # TODO(JP): remove deprecated field
    driver = models.ForeignKey(Driver, null=True) # TODO(JP): null=False after migration & backfill
    car = models.ForeignKey(Car, null=False)
    created_time = models.DateTimeField(auto_now_add=True)

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
