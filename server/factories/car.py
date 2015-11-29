# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import string
import datetime
from decimal import Decimal

from factory import LazyAttribute
from factory import SubFactory, SelfAttribute

from django.utils import timezone

from idlecars.factory_helpers import Factory, faker
from server.factories import Owner, BankAccountOwner, MakeModel, Insurance
from server import models


class Car(Factory):
    class Meta:
        model = 'server.Car'

    status = LazyAttribute(lambda o: random.choice(['available', 'unknown', 'busy']))
    make_model = SubFactory(MakeModel)
    year = LazyAttribute(lambda o: random.randint(2000, 2016))
    plate = LazyAttribute(lambda o: ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(8)]
    ))
    hybrid = LazyAttribute(lambda o: random.choice([True, False]))
    base = LazyAttribute(lambda o: ' '.join(faker.words(nb=3)).title())


class ClaimedCar(Car):
    ''' car that an owner has claimed and filled in details for '''
    owner = SubFactory(Owner)
    solo_cost = LazyAttribute(lambda o: Decimal(random.randint(8, 16) * 50))
    solo_deposit = SelfAttribute('solo_cost')
    min_lease = '_02_one_week'
    next_available_date = LazyAttribute(
        lambda o: timezone.now().date() - datetime.timedelta(days=random.randint(1, 10))
    )


class BookableCar(ClaimedCar):
    owner = SubFactory(BankAccountOwner)
    status = models.Car.STATUS_AVAILABLE


class CarExpiredListing(BookableCar):
    next_available_date = timezone.now().date() - datetime.timedelta(days=30)
    last_status_update = timezone.now().date() - datetime.timedelta(days=30)


class CompleteCar(BookableCar):
    ''' creates a car with all optional fields filled in '''
    hybrid = True
    exterior_color = LazyAttribute(lambda o: random.choice(range(5)))
    interior_color = LazyAttribute(lambda o: random.choice(range(5)))
    last_known_mileage = LazyAttribute(lambda o: random.randint(10000, 80000))
    last_mileage_update = LazyAttribute(lambda o: faker.date_time_this_month())
    insurance = SubFactory(Insurance)
