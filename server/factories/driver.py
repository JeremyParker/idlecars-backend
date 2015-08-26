# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory, LazyAttribute, post_generation

from idlecars.factory_helpers import Factory, faker, make_item
from server.factories import AuthUser


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_approved = False
    auth_user = SubFactory(AuthUser, password='password')


class CompletedDriver(Driver):
    driver_license_image = LazyAttribute(lambda o: faker.url())
    fhv_license_image = LazyAttribute(lambda o: faker.url())
    address_proof_image = LazyAttribute(lambda o: faker.url())
    defensive_cert_image = LazyAttribute(lambda o: faker.url())
    documentation_approved = False

class PaymentMethodDriver(CompletedDriver):
    @post_generation
    def payment_method(self, create, count, **kwargs):
        self.braintree_customer_id = 'fake_customer_id'
        from server.factories import payment_method
        kwargs['driver'] = self
        payment_method = make_item(create, payment_method.PaymentMethod, **kwargs)
        # if not create:
        #     # Fiddle with django internals so self.deal_set.all() works even when building
        #     self._prefetched_objects_cache = {'payment_method': payment_method}
        #     self._payment_method = payment_method

class ApprovedDriver(PaymentMethodDriver):
    documentation_approved = True
