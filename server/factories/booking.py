# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute
from factory import SubFactory, SelfAttribute

from idlecars.factory_helpers import Factory, faker
from server.factories import BookableCar, ApprovedDriver, UserAccount

class Booking(Factory):
    class Meta:
        model = 'server.Booking'

    car = SubFactory(BookableCar)
    driver = SubFactory(ApprovedDriver)
