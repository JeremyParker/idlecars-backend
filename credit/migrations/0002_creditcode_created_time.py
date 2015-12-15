# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('credit', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditcode',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 15, 22, 44, 28, 119253, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
