# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from consumable_token import ConsumableToken
import server.models


class Renewal(ConsumableToken):
    car = models.ForeignKey(server.models.Car, related_name='renewals')
