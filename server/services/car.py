# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db.models import Q

from server import models


next_available_date_threshold = datetime.date.today() + datetime.timedelta(days=30)
staleness_threshold = datetime.date.today() - datetime.timedelta(days=3)

def filter_data_complete(queryset):
    '''
    return cars whose data is complete for the purposes of showing in listings.
    '''
    return queryset.filter(
            owner__isnull=False,
            make_model__isnull=False,
            year__isnull=False,
            solo_cost__isnull=False,
            solo_deposit__isnull=False,
            owner__last_engagement__isnull=False,
        ).exclude(
            Q(min_lease='_00_unknown') |
            Q(plate='') |
            Q(base='') |
            Q(owner__city='') |
            Q(owner__state_code='') |
            Q(owner__zipcode='')
        )


def filter_bookable(queryset):
    '''
    return cars whose status is known, aren't busy through elsewhere, and don't have a booking 
    in progress.
    '''
    return queryset.filter(
        Q(status=models.Car.STATUS_AVAILABLE) |
        Q(status=models.Car.STATUS_BUSY, next_available_date__lt=next_available_date_threshold)
    ).exclude(
        Q(booking__state__in=[
            models.Booking.COMPLETE,
            models.Booking.REQUESTED,
            models.Booking.ACCEPTED,
        ])
    )


def filter_not_stale(queryset):
    '''
    return cars whose owners have been contacted in the last few days, so we know the car's state.
    '''
    return queryset.exclude(owner__last_engagement__lt=staleness_threshold)


def filter_stale(queryset):
    '''
    return cars whose owners haven't been contacted in the last few days, so the car's state 
    is stale.
    '''
    return queryset.filter(owner__last_engagement__lt=staleness_threshold)


listing_queryset = filter_not_stale(filter_bookable(filter_data_complete(models.Car.objects.all())))
