# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import datetime
import string

from factory import SubFactory, LazyAttribute
from django.utils import timezone

from idlecars.factory_helpers import Factory, faker, make_item
from server.factories import Driver


class RejectedPaymentMethod(Factory):
    class Meta:
        model = 'server.PaymentMethod'
    driver = SubFactory(Driver)


class PaymentMethod(RejectedPaymentMethod):
    gateway_token = LazyAttribute(lambda o: ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(8)]
    ))
    suffix = LazyAttribute(lambda o: ''.join([random.choice(string.digits) for i in range(4)]))
    card_type = random.choice(['Mastercard', 'VISA'])
    card_logo = 'https://assets.braintreegateway.com/payment_method_logo/visa.png?environment=sandbox'
    expiration_date = timezone.now() + datetime.timedelta(days=random.randint(100, 500))
