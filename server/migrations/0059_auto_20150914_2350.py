# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0058_auto_20150914_1734'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='week_ending',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Pre-authorized'), (3, 'In Escrow'), (4, 'Voided'), (5, 'Payment declined'), (6, 'Card rejected')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(max_length=32, blank=True),
        ),
    ]
