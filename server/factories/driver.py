# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory

from idlecars.factory_helpers import Factory
from . import AuthUser


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_complete = False
    auth_user = SubFactory(AuthUser, password='password')


class CompletedDriver(Driver):
    documentation_complete = True
