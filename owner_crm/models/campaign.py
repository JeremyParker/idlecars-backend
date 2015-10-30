# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from idlecars import model_helpers


class Campaign(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length = 255)

    SMS_METHOD = 0
    EMAIL_METHOD = 1

    METHOD_CHOICES = [
        (SMS_METHOD, 'SMS'),
        (EMAIL_METHOD, 'Email'),
    ]

    preferred_method = models.IntegerField(
        choices=METHOD_CHOICES,
        default=0,
    )

    notes = models.TextField(blank=True)
