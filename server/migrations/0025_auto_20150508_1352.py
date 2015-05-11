# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0024_auto_20150501_1556'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='owner',
            name='last_engagement',
        ),
        migrations.AddField(
            model_name='car',
            name='last_status_update',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 10, 17, 52, 5, 541097, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
