# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import string
from decimal import Decimal

from factory import LazyAttribute
from factory import SubFactory, SelfAttribute

from idlecars.factory_helpers import Factory
from server.factories import Owner, MakeModel

class Car(Factory):
    class Meta:
        model = 'server.Car'

    owner = SubFactory(Owner)
    status = LazyAttribute(lambda o: random.choice(['available', 'unknown', 'busy']))
    make_model = SubFactory(MakeModel)
    year = LazyAttribute(lambda o: random.randint(2000, 2016))
    plate = LazyAttribute(lambda o: ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(8)]
    ))
    solo_cost = LazyAttribute(lambda o: Decimal(random.randint(8, 16) * 5000) / Decimal(100))
    solo_deposit = SelfAttribute('solo_cost')
