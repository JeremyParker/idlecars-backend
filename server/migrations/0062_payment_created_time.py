# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0061_auto_20150916_1154'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 16, 19, 58, 38, 790353, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
