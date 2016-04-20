# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import string

from factory import SubFactory, LazyAttribute, post_generation

from idlecars.factory_helpers import Factory, faker, make_item
from idlecars.factories import AuthUser
from credit.factories import CreditCode


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_approved = False
    auth_user = SubFactory(AuthUser, password='password')


class CompletedDriver(Driver):
    ssn = LazyAttribute(lambda o: ''.join([random.choice(string.digits) for i in range(9)]))
    driver_license_image = LazyAttribute(lambda o: faker.url())
    fhv_license_image = LazyAttribute(lambda o: faker.url())
    address_proof_image = LazyAttribute(lambda o: faker.url())
    defensive_cert_image = LazyAttribute(lambda o: faker.url())
    documentation_approved = False
