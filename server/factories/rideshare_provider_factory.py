# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory, faker


class RideshareFlavorFactory(Factory):
    class Meta:
        model = 'server.RideshareFlavor'
    name = LazyAttribute(lambda o: faker.last_name())
    friendly_id = LazyAttribute(lambda o: faker.last_name())
