# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0071_braintreerequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='sms_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='sms_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
