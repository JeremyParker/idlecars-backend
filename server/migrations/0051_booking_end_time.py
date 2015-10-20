# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0050_auto_20150806_0932'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='end_time',
            field=models.DateTimeField(null=True),
        ),
    ]
