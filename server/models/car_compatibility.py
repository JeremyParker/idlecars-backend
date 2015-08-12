# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import RideshareFlavor

class CarCompatibility(object):
    def __init__(self, car):
        self.car = car
        self._compatible_flavors = None

    def uber_x(self):
        return self._compatible_flavor_name('uber_x')

    def uber_xl(self):
        return self._compatible_flavor_name('uber_xl')

    def uber_black(self):
        return self._compatible_flavor_name('uber_black')

    def uber_suv(self):
        return self._compatible_flavor_name('uber_suv')

    def lyft_standard(self):
        if self.car.make_model.passenger_count < 6:
            return RideshareFlavor.objects.get(friendly_id='lyft_standard').name

    def lyft_plus(self):
        if self.car.make_model.passenger_count >= 6:
            return RideshareFlavor.objects.get(friendly_id='lyft_plus').name

    def via_standard(self):
        return self._compatible_flavor_name('via_standard')

    def gett_standard(self):
        if self.car.exterior_color in (0,1) and self.car.interior_color in (0,1,2):
            return RideshareFlavor.objects.get(friendly_id='gett_standard').name


    def _compatible_flavor_name(self, friendly_id):
        if not self._compatible_flavors:
            self._compatible_flavors = self._get_compatible_flavors()

        return self._compatible_flavors.get(friendly_id)

    def _get_compatible_flavors(self):
        return {
            flavor.friendly_id: flavor.name for flavor in self.car.make_model.rideshareflavor_set.all()
        }
