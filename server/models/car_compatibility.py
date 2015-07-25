# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

class CarCompatibility(object):
    def __init__(self, car):
        self.car = car

    def uber_x(self):
        return self._model_is_compatible('uber_x') and self.car.year > 2009

    def _model_is_compatible(self, frieldly_id):
        return self.car.make_model.rideshare_provider_set.filter(frieldly_id=frieldly_id).exists()
