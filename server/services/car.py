# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from idlecars import model_helpers

from server.models import Booking, Car
from . import car_helpers, make_model_service
import tlc_data_service


class CarTLCException(Exception):
    pass


class CarDuplicateException(Exception):
    pass


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


def create_car(owner, plate):
    new_car = Car(plate=plate)
    try:
        tlc_data_service.lookup_fhv_data(new_car)
    except Car.DoesNotExist:
        raise CarTLCException

    car, is_new = Car.objects.get_or_create(plate=new_car.plate)
    if not is_new:
        raise CarDuplicateException()

    model_helpers.copy_fields(new_car, car, tlc_data_service.fhv_fields)

    car.status = Car.STATUS_AVAILABLE
    car.next_available_date = timezone.localtime(timezone.now()).date()
    car.owner = owner
    car.save()
    return car
