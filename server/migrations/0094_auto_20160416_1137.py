# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0093_remove_booking_deprecated_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='shift_details',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='shift',
            field=models.IntegerField(default=0, choices=[(0, 'Unknown'), (1, '24/7.'), (2, 'Day shift.'), (3, 'Night shift.'), (4, '')]),
        ),
    ]
