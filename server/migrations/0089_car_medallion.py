# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0088_auto_20151231_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='medallion',
            field=models.BooleanField(default=False),
        ),
    ]
