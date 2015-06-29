# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models
from . import car_helpers


def filter_live(queryset):
    return car_helpers._filter_not_stale(
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(queryset)))


def filter_needs_renewal(queryset):
    return car_helpers._filter_stale(
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(queryset)))


def filter_booking_in_progress(queryset):
    return queryset.filter(car_helpers.q_booking_in_progress)


listing_queryset = filter_live(models.Car.objects.all())


def get_stale_within(minutes_until_stale):
    '''
    Returns a list of cars whose listings will expire soon
    '''
    return car_helpers._filter_stale_within(
        minutes_until_stale,
        car_helpers._filter_data_complete(
            car_helpers._filter_bookable(
                models.Car.objects.all())))


def get_image_url(car):
    return 'https://s3.amazonaws.com/images.idlecars.com/{}'.format(car.make_model.image_filename)
