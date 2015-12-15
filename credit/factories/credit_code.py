# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random
import string
from decimal import Decimal

from factory import LazyAttribute

from idlecars.factory_helpers import Factory


class CreditCode(Factory):
    class Meta:
        model = 'credit.CreditCode'

    credit_code = LazyAttribute(lambda o: ''.join(
        [random.choice(string.ascii_uppercase + string.digits) for i in range(4)]
    ))
    credit_amount = LazyAttribute(lambda o: Decimal(random.randint(1, 5) * 10))
    invitor_credit_amount = LazyAttribute(lambda o: Decimal(random.randint(1, 5) * 10))
