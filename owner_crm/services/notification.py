# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from . import ops_notifications, driver_notifications, owner_notifications, street_team_notifications


def send(campaign_name, argument):
    clas = eval(campaign_name)(campaign_name, argument)

    clas.send()

