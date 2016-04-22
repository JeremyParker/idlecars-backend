# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.conf import settings
from django.db.models import Q

from server.models import Booking, Car, Owner


next_available_date_threshold = timezone.now() + datetime.timedelta(days=120)
staleness_threshold = timezone.now() - datetime.timedelta(days=settings.STALENESS_LIMIT)

# TODO - this belongs in booking_service
def _filter_booking_in_progress(booking_queryset):
    return booking_queryset.filter(
        requested_time__isnull=False,
        refund_time__isnull=True,
        incomplete_time__isnull=True,
)

def _filter_data_complete(queryset):
    '''
    return cars whose data is complete for the purposes of showing in listings.
    '''
    return queryset.filter(
            owner__isnull=False,
            make_model__isnull=False,
            year__isnull=False,
            weekly_rent__isnull=False,
            deposit__isnull=False,
        ).exclude(
            Q(owner__zipcode='')
        )


def is_data_complete(car):
    '''
    this checks the same logic as above for an individual car
    '''
    return car.owner and car.make_model and car.year and car.weekly_rent and car.deposit != None and car.owner.zipcode


def _filter_bookable(queryset):
    '''
    return cars that aren't busy through elsewhere, don't have a booking
    in progress.
    '''
    # TODO - we probably need to optimize this, or at least cache it
    active_bookings = _filter_booking_in_progress(Booking.objects.all())
    booked_car_ids = [b.car.id for b in active_bookings]
    return queryset.filter(
        next_available_date__isnull=False,
        next_available_date__lt=next_available_date_threshold,
    ).exclude(
        id__in=booked_car_ids
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


def is_stale(car):
    return car.last_status_update <= staleness_threshold


def _filter_stale_within(minutes_until_stale, queryset):
    '''
    return cars whose state will be stale soon, but aren't yet stale
    '''
    stale_soon_threshold = staleness_threshold + datetime.timedelta(minutes=minutes_until_stale)
    return queryset.filter(
        last_status_update__lt=stale_soon_threshold,
        last_status_update__gte=staleness_threshold,
    )
