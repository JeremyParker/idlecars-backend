# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import MakeModel

def lookup_vin_data(car):
    car.make_model = MakeModel.objects.first()
