# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings


def renewal_url(renewal):
    parts = (settings.DRIVER_APP_URL, '#', 'listings', unicode(renewal.car.id), 'renewals', renewal.token)
    return '/'.join(parts)

def doc_upload_url():
    parts = (settings.DRIVER_APP_URL, '#', 'bookings')
    return '/'.join(parts)

def car_listing_url():
    parts = (settings.DRIVER_APP_URL, '#', 'listings')
    return '/'.join(parts)

def car_details_url(car):
    parts = (car_listing_url(), unicode(car.pk))
    return '/'.join(parts)

def bookings():
    parts = (settings.DRIVER_APP_URL, '#', 'account', 'bookings')
    return '/'.join(parts)

def password_reset(password_reset):
    parts = (settings.DRIVER_APP_URL, '#', 'reset_password', password_reset.token)
    return '/'.join(parts)

def driver_account():
    parts = (settings.DRIVER_APP_URL, '#', 'account')
    return '/'.join(parts)

def driver_login():
    return bookings()

def driver_signup():
    parts = (settings.DRIVER_APP_URL, '#', 'users', 'new', 'phone_number')
    return '/'.join(parts)

# TODO - remove this
def owner_password_reset(password_reset):
    parts = (settings.DRIVER_APP_URL, '#', 'owner_reset_password', password_reset.token)
    return '/'.join(parts)

def terms_of_service():
    parts = (settings.DRIVER_APP_URL, '#', 'terms_of_service')
    return '/'.join(parts)

def faq():
    parts = (settings.DRIVER_APP_URL, '#', 'driver_faq')
    return '/'.join(parts)

# TODO - remove this
def add_car_form():
    return 'https://goo.gl/NhIGM6'

