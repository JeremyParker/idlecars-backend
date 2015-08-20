# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute
from factory import SubFactory, SelfAttribute

from django.utils import timezone

from idlecars.factory_helpers import Factory, faker
from server.factories import BookableCar, ApprovedDriver, UserAccount
from server import models

class Booking(Factory):
    class Meta:
        model = 'server.Booking'

    car = SubFactory(BookableCar)
    driver = SubFactory(ApprovedDriver)


class ReservedBooking(Booking):
    checkout_time = timezone.now()


class RequestedBooking(ReservedBooking):
    requested_time = timezone.now()


class AcceptedBooking(RequestedBooking):
    approval_time = timezone.now()


class BookedBooking(AcceptedBooking):
    pickup_time = timezone.now()


class ReturnedBooking(BookedBooking):
    return_time = timezone.now()


class RefundedBooking(ReturnedBooking):
    refund_time = timezone.now()


class IncompleteBooking(Booking):
    incomplete_time = timezone.now()
    incomplete_reason = models.Booking.REASON_CANCELED
