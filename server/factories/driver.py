# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory

from idlecars.factory_helpers import Factory


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_complete = False


class CompletedDriver(Driver):
    documentation_complete = True
