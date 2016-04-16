# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0094_auto_20160416_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='shift_details',
            field=models.CharField(default='', max_length=128, blank=True),
        ),
    ]
