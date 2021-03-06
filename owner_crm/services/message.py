# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import sys

from owner_crm.models import Message


def get_booking_kwargs(obj):
    return {
        'car': obj.car,
        'owner': obj.car.owner,
        'driver': obj.driver,
        'booking': obj,
    }

def get_driver_kwargs(obj):
    return { 'driver': obj, }


def get_car_kwargs(obj):
    return { 'car': obj, }


def get_owner_kwargs(obj):
    return { 'owner': obj, }

def get_onboardingowner_kwargs(obj):
    return { 'onboarding_owner': obj }

def log_message(campaign_name, key_obj):
    kwargs_func_name = 'get_{}_kwargs'.format(key_obj.__class__.__name__).lower()
    kwargs_func = getattr(sys.modules[__name__], kwargs_func_name)
    kwargs = kwargs_func(key_obj)
    kwargs.update({'campaign': campaign_name,})
    Message.objects.create(**kwargs)
