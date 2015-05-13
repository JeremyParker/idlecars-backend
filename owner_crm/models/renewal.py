# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import uuid
import base64

from django.db import models

import server.models


def _generate_token():
    return base64.b64encode(uuid.uuid4().bytes).replace('=', '')


class Renewal(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    car = models.ForeignKey(server.models.Car, related_name='renewals')

    STATE_PENDING = 1
    STATE_RENEWED = 2
    STATE = (
        (STATE_PENDING, 'Pending'),
        (STATE_RENEWED, 'Renewed'),
    )
    state = models.IntegerField(choices=STATE, default=STATE_PENDING)

    token = models.CharField(
        max_length=40,
        default=_generate_token,
        db_index=True,
    )
