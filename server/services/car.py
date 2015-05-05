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
        Q(status=models.Car.STATUS_AVAILABLE) |
        Q(status=models.Car.STATUS_BUSY, next_available_date__lt=date_threshold)
    ).exclude(
        Q(min_lease='_00_unknown') |
        Q(plate='') |
        Q(base='') |
        Q(owner__city='') |
        Q(owner__state_code='') |
        Q(owner__zipcode='') |
        Q(booking__state__in=[
            models.Booking.COMPLETE,
            models.Booking.REQUESTED,
            models.Booking.ACCEPTED,
        ])
    )
