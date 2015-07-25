# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker


class RideshareProviderFactory(Factory):
    class Meta:
        model = 'server.RideshareProvider'
    name = LazyAttribute(lambda o: faker.last_name())
    frieldly_id = LazyAttribute(lambda o: faker.last_name())
