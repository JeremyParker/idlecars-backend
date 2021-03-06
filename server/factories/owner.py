# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random, string
import datetime

from factory import LazyAttribute, RelatedFactory, post_generation

from idlecars.factory_helpers import Factory, faker
from server.models import Owner as owner_model
from idlecars.factories import AuthUser


class Owner(Factory):
    class Meta:
        model = 'server.Owner'

    company_name = LazyAttribute(lambda o: faker.name() + "'s Cars")
    address1 = faker.street_address
    city = LazyAttribute(lambda o: faker.city())
    state_code = LazyAttribute(lambda o: faker.state_abbr())
    zipcode = LazyAttribute(lambda o: faker.zipcode())
    rating = random.choice(owner_model.RATING)[0]
    social = LazyAttribute(lambda o: ''.join(
        [random.choice(string.digits) for i in range(4)]
    ))

    @post_generation
    def auth_user(self, create, value, **kwargs):
        auth_user = AuthUser.create(password='password')
        self.auth_users.add(auth_user)
