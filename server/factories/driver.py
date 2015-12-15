# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import SubFactory, LazyAttribute, post_generation

from idlecars.factory_helpers import Factory, faker, make_item
from idlecars.factories import AuthUser

from credit.factories import CreditCode


class Driver(Factory):
    class Meta:
        model = 'server.Driver'
    documentation_approved = False
    base_letter_rejected = False
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
        from server.factories.payment_method import PaymentMethod
        kwargs['driver'] = self
        payment_method = make_item(create, PaymentMethod, **kwargs)


class ApprovedDriver(PaymentMethodDriver):
    documentation_approved = True

    @post_generation
    def invite_code(self, create, count, **kwargs):
        self.auth_user.customer.invite_code = CreditCode.create()


class BaseLetterDriver(ApprovedDriver):
    base_letter = LazyAttribute(lambda o: faker.url())
