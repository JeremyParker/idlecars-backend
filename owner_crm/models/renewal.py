# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import uuid
import base64

from django.db import models

import server.models


def _generate_token():
    return base64.b64encode(uuid.uuid4().bytes).replace('=', '')


class Renewal(models.Model):
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    updated_time = models.DateTimeField(auto_now=True, null=True)

    car = models.ForeignKey(server.models.Car, blank=True, null=True, related_name='renewals')

    PENDING_STATE = 1
    RENEWED_STATE = 2
    STATE = (
        (PENDING_STATE, 'Pending'),
        (RENEWED_STATE, 'Renewed'),
    )
    state = models.IntegerField(choices=STATE, default=PENDING_STATE)

    token = models.CharField(
        max_length=40,
        default=_generate_token,
        db_index=True,
        unique=True,
    )
