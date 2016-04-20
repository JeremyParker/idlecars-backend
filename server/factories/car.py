# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import string
import datetime
from decimal import Decimal

from factory import LazyAttribute
from factory import SubFactory, SelfAttribute

from django.utils import timezone
from django.conf import settings

from idlecars.factory_helpers import Factory, faker
from server.factories import Owner, Owner, MakeModel, Insurance
from server import models


class Car(Factory):
    class Meta:
        model = 'server.Car'

    make_model = SubFactory(MakeModel)
    year = LazyAttribute(lambda o: random.randint(2000, 2016))
    plate = LazyAttribute(lambda o: ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(8)]
    ))
    hybrid = LazyAttribute(lambda o: random.choice([True, False]))
    # base = LazyAttribute(lambda o: ' '.join(faker.words(nb=3)).title())
    shift = models.Car.SHIFT_UNKNOWN


class BookableCar(Car):
    ''' car that an owner has claimed and filled in details for '''
    owner = SubFactory(Owner)
    weekly_rent = LazyAttribute(lambda o: Decimal(random.randint(8, 16) * 50))
    deposit = SelfAttribute('weekly_rent')
    next_available_date = LazyAttribute(
        lambda o: timezone.now() - datetime.timedelta(days=random.randint(1, 10))
    )


class CarExpiredListing(BookableCar):
    next_available_date = timezone.now() - datetime.timedelta(days=30)
    last_status_update = timezone.now() - datetime.timedelta(days=settings.STALENESS_LIMIT + 1)


class CompleteCar(BookableCar):
    ''' creates a car with all optional fields filled in '''
    hybrid = True
    last_known_mileage = LazyAttribute(lambda o: random.randint(10000, 80000))
    last_mileage_update = LazyAttribute(lambda o: faker.date_time_this_month())
    insurance = SubFactory(Insurance)
