# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import datetime

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker
from server.models import Owner as owner_model


class Owner(Factory):
    class Meta:
        model = 'server.Owner'

    company_name = LazyAttribute(lambda o: faker.name() + "'s Cars")
    address1 = faker.street_address
    city = LazyAttribute(lambda o: faker.city())
    state_code = LazyAttribute(lambda o: faker.state_abbr())
    zipcode = LazyAttribute(lambda o: faker.zipcode())
    rating = random.choice(owner_model.RATING)[0]
