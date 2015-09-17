# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import RideshareFlavor

class CarCompatibility(object):
    def __init__(self, car):
        self.car = car
        self._compatible_flavors = None
        self._flavor_names = None

    def all(self):
        services = (
            self.uber_x,
            self.uber_xl,
            self.uber_black,
            self.uber_suv,
            self.lyft_standard,
            self.lyft_plus,
            self.via_standard,
            self.gett_standard,
        )
        return [method() for method in services if method()]

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
            return self._flavor_name('lyft_standard')

    def lyft_plus(self):
        if self.car.make_model.passenger_count >= 6:
            return self._flavor_name('lyft_plus')

    def via_standard(self):
        return self._compatible_flavor_name('via_standard')

    def gett_standard(self):
        if self.car.exterior_color in (0,1) and self.car.interior_color in (0,1,2):
            return self._flavor_name('gett_standard')


    def _compatible_flavor_name(self, friendly_id):
        if not self._compatible_flavors:
            self._compatible_flavors = self._get_compatible_flavors()

        return self._compatible_flavors.get(friendly_id)

    def _get_compatible_flavors(self):
        return {
            flavor.friendly_id: flavor.friendly_id for flavor in self.car.make_model.rideshareflavor_set.all()
        }

    def _flavor_name(self, friendly_id):
        if not self._flavor_names:
            self._flavor_names = self._get_flavor_names()

        return self._flavor_names.get(friendly_id)

    def _get_flavor_names(self):
        return {
            flavor.friendly_id: flavor.name for flavor in RideshareFlavor.objects.all()
        }
