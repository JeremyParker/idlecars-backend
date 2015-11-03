# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from . import ops_notifications, driver_notifications, owner_notifications, street_team_notifications


def send(function_name, argument):
    clas = eval(function_name)(function_name, argument)

    clas.send()

