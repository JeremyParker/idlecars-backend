# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def renewal_url(renewal):
    parts = (settings.WEBAPP_URL, '#', 'cars', renewal.car.id, 'renewals', renewal.id)
    return '/'.join(parts)
