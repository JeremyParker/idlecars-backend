# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0083_auto_20151218_1204'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='split_cost',
        ),
        migrations.RemoveField(
            model_name='car',
            name='split_deposit',
        ),
    ]
