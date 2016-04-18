# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal
from factory import LazyAttribute
from factory import SubFactory, SelfAttribute, post_generation

from django.utils import timezone

from idlecars.factory_helpers import Factory, faker
from server.factories import BookableCar, CompletedDriver, CompletedDriver, CompletedDriver
from server.factories import Payment, PreAuthorizedPayment, HeldInEscrowPayment, SettledPayment
from server import models

class Booking(Factory):
    class Meta:
        model = 'server.Booking'

    car = SubFactory(BookableCar)
    driver = SubFactory(CompletedDriver)
    end_time = LazyAttribute(lambda o: (timezone.now() + datetime.timedelta(days=7 * 6)).replace(
        hour = 0,
        minute = 0,
        second = 0,
        microsecond = 0,
    ))


class RequestedBooking(Booking):
    requested_time = LazyAttribute(lambda o: timezone.now())


class ReturnedBooking(RequestedBooking):
    approval_time = LazyAttribute(lambda o: timezone.now())


class RefundedBooking(ReturnedBooking):
    refund_time = LazyAttribute(lambda o: timezone.now())


class IncompleteBooking(Booking):
    incomplete_time = LazyAttribute(lambda o: timezone.now())
    incomplete_reason = models.Booking.REASON_CANCELED
