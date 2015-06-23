# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.db.models import Q

from server import models


next_available_date_threshold = timezone.now().date() + datetime.timedelta(days=30)
staleness_threshold = timezone.now() - datetime.timedelta(days=4)

q_booking_in_progress = Q(booking__state__in=[
    models.Booking.COMPLETE,
    models.Booking.REQUESTED,
    models.Booking.ACCEPTED,
])


def _filter_data_complete(queryset):
    '''
    return cars whose data is complete for the purposes of showing in listings.
    '''
    return queryset.filter(
            owner__isnull=False,
            make_model__isnull=False,
            year__isnull=False,
            solo_cost__isnull=False,
            solo_deposit__isnull=False,
        ).exclude(
            Q(min_lease='_00_unknown') |
            Q(plate='') |
            Q(base='') |
            Q(owner__city='') |
            Q(owner__state_code='') |
            Q(owner__zipcode='')
        )


def _filter_bookable(queryset):
    '''
    return cars whose status is known, aren't busy through elsewhere, and don't have a booking
    in progress.
    '''
    return queryset.filter(
        Q(status=models.Car.STATUS_AVAILABLE) |
        Q(status=models.Car.STATUS_BUSY, next_available_date__lt=next_available_date_threshold)
    ).exclude(
        q_booking_in_progress
    )


def _filter_not_stale(queryset):
    '''
    return cars whose owners have been contacted in the last few days, so we know the car's state.
    '''
    return queryset.filter(last_status_update__gte=staleness_threshold)


def _filter_stale(queryset):
    '''
    return cars whose owners haven't been contacted in the last few days, so the car's state
    is stale.
    '''
    return queryset.filter(last_status_update__lt=staleness_threshold)


def _filter_stale_within(minutes_until_stale, queryset):
    '''
    return cars whose state will be stale soon, but aren't yet stale
    '''
    stale_soon_threshold = staleness_threshold + datetime.timedelta(minutes=minutes_until_stale)
    return queryset.filter(
        last_status_update__lt=stale_soon_threshold,
        last_status_update__gte=staleness_threshold,
    )
