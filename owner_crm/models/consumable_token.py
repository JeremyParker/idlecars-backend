# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import random, string

from django.db import models

import server.models


def _generate_token():
    choices = string.uppercase + string.lowercase + string.digits
    return ''.join(random.SystemRandom().choice(choices) for _ in xrange(20))


class ConsumableToken(models.Model):
    class Meta:
        abstract = True

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    STATE_PENDING = 1
    STATE_CONSUMED = 2
    STATE_RETRACTED = 3
    STATE = (
        (STATE_PENDING, 'Pending'),
        (STATE_CONSUMED, 'Consumed'),
        (STATE_RETRACTED, 'Retracted'),
    )
    state = models.IntegerField(choices=STATE, default=STATE_PENDING)

    token = models.CharField(
        max_length=40,
        default=_generate_token,
        db_index=True,
    )
