# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0085_car_shift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='shift',
            field=models.IntegerField(default=1, choices=[(0, 'Unknown'), (1, '24/7'), (2, 'Day shift (5am-5pm)'), (3, 'Night shift (5pm-5am)')]),
        ),
    ]
