# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0017_car_base'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='solo_cost',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='solo_deposit',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='split_cost',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='split_deposit',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
            preserve_default=True,
        ),
    ]
