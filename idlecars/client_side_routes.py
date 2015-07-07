# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def renewal_url(renewal):
    parts = (settings.WEBAPP_URL, '#', 'cars', unicode(renewal.car.id), 'renewals', renewal.token)
    return '/'.join(parts)

def doc_upload_url():
    parts = (settings.WEBAPP_URL, '#', 'bookings')
    return '/'.join(parts)

def car_listing_url():
    parts = (settings.WEBAPP_URL, '#', 'cars')
    return '/'.join(parts)

def car_details_url(car):
    parts = (car_listing_url(), unicode(car.pk))
    return '/'.join(parts)
