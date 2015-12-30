# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0086_auto_20151218_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='weekly_rent',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
    ]
