# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from insurance import Insurance
from user_account import UserAccount
from owner import Owner
from make_model import MakeModel
from car import Car
from driver import Driver
from booking import Booking
from rideshare_provider import RideshareProvider


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
