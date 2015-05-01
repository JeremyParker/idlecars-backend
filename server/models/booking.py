# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .user_account import UserAccount
from .car import Car


class Booking(models.Model):
    user_account = models.OneToOneField(UserAccount)
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

    STATE = (
        (PENDING, 'Pending - waiting for driver docs'),
        (COMPLETE, 'Complete - checking driver creds'),
        (REQUESTED, 'Requested - waiting for owner/insurance'),
        (ACCEPTED, 'Accepted - waiting for deposit, ssn, contract'),
        (BOOKED, 'Booked - car marked busy with new available_time'),
        (FLAKE, 'Flake - Never Submitted Docs'),
        (TOO_SLOW, 'Too Slow - driver took too long to submit docs'),
        (OWNER_REJECTED, 'Owner Rejected - driver wasn\t approved'),
        (DRIVER_REJECTED, 'Driver Rejected - driver changed their mind'),
        (MISSED, 'Missed - car rented out before we found a driver'),
    )
    state = models.IntegerField(choices=STATE, default=PENDING)
    notes = models.TextField(blank=True)
