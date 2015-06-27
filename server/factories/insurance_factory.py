# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute
from idlecars.factory_helpers import Factory, faker

class Insurance(Factory):
    class Meta:
        model = 'server.Insurance'

    insurer_name = LazyAttribute(lambda o: faker.company())
