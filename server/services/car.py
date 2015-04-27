# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models

class Car:
    queryset = models.Car.objects.filter(
        owner__isnull=False,
        make_model__isnull=False,
        year__isnull=False,
        solo_cost__isnull=False,
        solo_deposit__isnull=False,
    ).exclude(
        min_lease='_00_unknown',
    ).exclude(
        status='unknown',
    ).exclude(
        next_available_date__isnull=True,
        status='busy',
    ).exclude(
        plate='',
    ).exclude(
        base='',
    ).exclude(
        owner__city='',
    ).exclude(
        owner__state_code='',
    ).exclude(
        booking__state=models.Booking.REQUESTED
    )
