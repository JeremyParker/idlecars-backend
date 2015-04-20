# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from .user_account import UserAccount
from .car import Car


class Booking(models.Model):
    user_account = models.OneToOneField(UserAccount)
    car = models.ForeignKey(Car, null=False)
    created_time = models.DateTimeField(auto_now_add=True)
