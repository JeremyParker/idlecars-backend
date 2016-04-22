# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models
from server.models import CarCompatibility

def get_cost_bucket(car):
    if car.weekly_rent < 40:
        return ['cheap']
    elif car.weekly_rent < 70:
        return ['medium']
    else:
        return ['pricey']


def search_attrs(car):
    return {
        'cost_bucket': get_cost_bucket(car),
        'body_type': _body_type(car),
        'lux_level': _lux_level(car),
        'work_with': _work_with(car),
    }

def _body_type(car):
    return ['Sedan'] if car.make_model.body_type == 0 else ['SUV']

def _lux_level(car):
    return ['Standard'] if car.make_model.lux_level == 0 else ['Luxury']

def _work_with(car):
    return CarCompatibility(car).all()
