# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models

def get_cost_bucket(car):
    if car.normalized_cost() < 60:
        return 'cheap'
    elif car.normalized_cost() < 80:
        return 'medium'
    else:
        return 'pricey'


def search_attrs(car):
    return {
        'cost_bucket': get_cost_bucket(car),
        'body_type': _body_type(car),
        'lux_level': _lux_level(car),
    }

def _body_type(car):
    return 'Sedan' if car.make_model.body_type == 0 else 'SUV'

def _lux_level(car):
    return 'Standard' if car.make_model.lux_level == 0 else 'Luxury'
