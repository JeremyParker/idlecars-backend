# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0077_auto_20151130_1909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='last_known_mileage',
            field=models.CommaSeparatedIntegerField(max_length=32, null=True, blank=True),
        ),
    ]
