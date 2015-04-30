# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db.models import Q

from server import models

class Car:
    date_threshold = datetime.date.today() + datetime.timedelta(days=30)
    queryset = models.Car.objects.filter(
        owner__isnull=False,
        make_model__isnull=False,
        year__isnull=False,
        solo_cost__isnull=False,
        solo_deposit__isnull=False,
    ).filter(
        Q(status='available') |
        Q(status='busy', next_available_date__lt=date_threshold)
    ).exclude(
        min_lease='_00_unknown',
    ).exclude(
        plate='',
    ).exclude(
        base='',
    ).exclude(
        owner__city='',
    ).exclude(
        owner__state_code='',
    ).exclude(
        booking__state__in=[
            models.Booking.COMPLETE,
            models.Booking.REQUESTED,
            models.Booking.ACCEPTED,
        ]
    )
