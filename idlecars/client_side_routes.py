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

def password_reset(password_reset):
    parts = (settings.WEBAPP_URL, '#', 'reset_password', password_reset.token)
    return '/'.join(parts)

def driver_account():
    parts = (settings.WEBAPP_URL, '#', 'account')
    return '/'.join(parts)

def owner_password_reset(password_reset):
    parts = (settings.WEBAPP_URL, '#', 'owner_reset_password', password_reset.token)
    return '/'.join(parts)

def terms_of_service():
    parts = (settings.WEBAPP_URL, '#', 'terms_of_service')
    return '/'.join(parts)

def add_car_form():
    return 'http://goo.gl/forms/4s26I6GUQY'
