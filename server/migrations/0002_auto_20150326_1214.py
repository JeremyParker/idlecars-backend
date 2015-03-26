# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fleetpartner',
            name='phone',
        ),
        migrations.AddField(
            model_name='fleetpartner',
            name='phone_number',
            field=models.CharField(help_text='Comma separated', max_length=256, db_column='phone', blank=True),
            preserve_default=True,
        ),
    ]
