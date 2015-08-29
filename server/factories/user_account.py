# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker
from idlecars.fields import parse_phone_number


class UserAccount(Factory):
    class Meta:
        model = 'server.UserAccount'

    first_name = LazyAttribute(lambda o: faker.first_name())
    last_name = LazyAttribute(lambda o: faker.last_name())
    phone_number = LazyAttribute(lambda o: parse_phone_number(faker.phone_number()))
    email = LazyAttribute(lambda o: o.first_name[0].lower() + o.last_name .lower()+ "@domain.com")
