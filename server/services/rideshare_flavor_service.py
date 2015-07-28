# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models

def get_rideshare_flavors(car):
    return car.make_model.rideshareflavor_set.filter(min_year__lt=car.year)
