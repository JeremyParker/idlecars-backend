# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
from decimal import Decimal

from factory import LazyAttribute, SubFactory

from idlecars.factory_helpers import Factory
from idlecars.factories import AuthUser


class Customer(Factory):
    class Meta:
        model = 'credit.Customer'

    user = SubFactory(AuthUser, password='password')
    invite_code = SubFactory(CreditCode)

    app_credit = LazyAttribute(lambda o: Decimal(random.randint(1, 5) * 10))


class InvitedCustomer(Customer):
  invitor_code = SubFactory(CreditCode)


class InvitorCreditedCustomer(InvitedCustomer)
  invitor_credited = True
