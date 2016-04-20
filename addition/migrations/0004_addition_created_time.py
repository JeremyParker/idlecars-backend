# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('addition', '0003_auto_20160420_1047'),
    ]

    operations = [
        migrations.AddField(
            model_name='addition',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 20, 19, 57, 22, 825686, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
