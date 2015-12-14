# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0076_auto_20151129_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='last_status_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='next_available_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
