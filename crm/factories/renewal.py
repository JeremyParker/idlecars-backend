# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory

import idlecars.factory_helpers
import server.factories

import crm.models

class Renewal(idlecars.factory_helpers.Factory):
    class Meta:
        model = 'crm.Renewal'

    car = SubFactory(server.factories.Car)
