# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker


class UserAccount(Factory):
    class Meta:
        model = 'server.UserAccount'

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())
    phone_number = LazyAttribute(lambda o: faker.phone_number())
    email = LazyAttribute(lambda o: o.first_name[0] + o.last_name + "@domain.com")
