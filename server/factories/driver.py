# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory, LazyAttribute

from idlecars.factory_helpers import Factory, faker
from . import AuthUser


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_approved = False
    auth_user = SubFactory(AuthUser, password='password')


class CompletedDriver(Driver):
    driver_license_image = LazyAttribute(lambda o: faker.url())
    fhv_license_image = LazyAttribute(lambda o: faker.url())
    address_proof_image = LazyAttribute(lambda o: faker.url())
    defensive_cert_image = LazyAttribute(lambda o: faker.url())
    documentation_approved = True
