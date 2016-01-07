# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal, ROUND_DOWN

from django.utils import timezone

from idlecars import model_helpers

from server.models import Booking, Car
from . import car_helpers, make_model_service
import tlc_data_service, vin_data_service


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
    in_progress_bookings = car_helpers._filter_booking_in_progress(Booking.objects.all())
    return queryset.filter(id__in=[b.car.id for b in in_progress_bookings])


def similar_cars(car):
    return Car.objects.filter(
        make_model=car.make_model,
        year=car.year,
        shift=car.shift,
        medallion=car.medallion,
    )


def has_booking_in_progress(car):
    in_progress_bookings = car_helpers._filter_booking_in_progress(Booking.objects.all())
    return car.id in [b.car.id for b in in_progress_bookings]


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


def recommended_rent(car):
    price = 0
    match_cars = similar_cars(car)
    convinced_price_cars = match_cars.filter(
        booking__checkout_time__isnull=False,
    ).order_by('weekly_rent')
    convinced_price_cars = convinced_price_cars[:convinced_price_cars.count() / 2]

    if convinced_price_cars:
        for car in convinced_price_cars:
            price += car.weekly_rent
        average_price = price / Decimal(convinced_price_cars.count())
        return average_price.quantize(Decimal('1'), rounding=ROUND_DOWN)

    attractive_price_cars = match_cars.filter(
        booking__isnull=False,
        booking__checkout_time__isnull=True,
        booking__incomplete_time__isnull=True,
    ).order_by('weekly_rent')
    attractive_price_cars = attractive_price_cars[:attractive_price_cars.count() / 2]

    if attractive_price_cars:
        for car in attractive_price_cars:
            price += car.weekly_rent
        average_price = price / attractive_price_cars.count()
        return average_price.quantize(Decimal('1'), rounding=ROUND_DOWN)

    listable_price_cars = match_cars.filter(
        booking__isnull=True,
    ).order_by('weekly_rent')
    listable_price_cars = listable_price_cars[:listable_price_cars.count() / 2]

    if listable_price_cars:
        for car in listable_price_cars:
            price += car.weekly_rent
        average_price = price * Decimal(0.9) / listable_price_cars.count()
        return average_price.quantize(Decimal('1'), rounding=ROUND_DOWN)

    return None


def create_car(owner, plate):
    car_info = Car(plate=plate)
    try:
        tlc_data_service.lookup_car_data(car_info)
    except Car.DoesNotExist:
        raise CarTLCException

    car, is_new = Car.objects.get_or_create(plate=car_info.plate)
    if not is_new and car.owner:
        raise CarDuplicateException()
    model_helpers.copy_fields(car_info, car, tlc_data_service.fhv_fields)

    try:
        vin_data_service.lookup_vin_data(car)
    except Car.DoesNotExist:
        # TODO - maybe we alert ops that this car needs to be looked up?
        pass

    try:
        tlc_data_service.lookup_insurance_data(car)
    except Car.DoesNotExist:
        # TODO - maybe we alert ops that this car needs to be looked up?
        pass

    car.next_available_date = timezone.now()
    car.last_status_update = timezone.now()
    car.owner = owner
    car.save()
    return car


def pre_save(modified_car, orig):
    if orig.next_available_date != modified_car.next_available_date:
        modified_car.last_status_update = timezone.now()

    if orig.last_known_mileage != modified_car.last_known_mileage:
        modified_car.last_mileage_update = timezone.now()

    if not orig.shift and modified_car.shift and not modified_car.weekly_rent:
        modified_car.weekly_rent = recommended_rent(modified_car)

    # if we're setting the cost for the first time, set a default solo deposit
    if modified_car.weekly_rent and not orig.weekly_rent:
        if not orig.deposit and not modified_car.deposit:
            modified_car.deposit = modified_car.weekly_rent / 4

    # if we're setting the car to unavailable, cancel any oustanding bookings
    if orig.next_available_date and not modified_car.next_available_date:
        from . import booking as booking_service
        booking_service.on_car_missed(modified_car)

    # if an owner is deleting their car, treat it like a missed car.
    if orig.owner and not modified_car.owner:
        from . import booking as booking_service
        booking_service.on_car_missed(modified_car)


def insurance(car, approved=False):
    from . import booking as booking_service
    bookings = Booking.objects.filter(car=car)
    booking = booking_service.filter_requested(bookings).first()
    if approved:
        booking_service.approve(booking)
    else:
        booking_service.reject(booking)
