# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import Booking, Car
from . import car_helpers, make_model_service


def filter_live(queryset):
    return car_helpers._filter_not_stale(
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(queryset)))


def filter_listable(queryset):
    ''' returns bookings that could be listed, but aren't. Either busy, owner bank unknown, etc '''
    return car_helpers._filter_data_complete(queryset)


def filter_needs_renewal(queryset):
    return car_helpers._filter_stale(
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(queryset)))


def filter_booking_in_progress(queryset):
    active_bookings = car_helpers._filter_booking_in_progress(Booking.objects.all())
    return queryset.filter(id__in=[b.car.id for b in active_bookings])


def get_stale_within(minutes_until_stale):
    '''
    Returns a list of live cars whose listings will expire soon
    '''
    return car_helpers._filter_stale_within(
        minutes_until_stale,
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(
                Car.objects.all())))


def get_image_url(car):
    return make_model_service.get_image_url(car.make_model, car.pk)
