# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0060_payment_service_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Pre-authorized'), (3, 'In Escrow'), (4, 'Payment refunded'), (5, 'Voided'), (6, 'Payment declined'), (7, 'Card rejected')]),
        ),
    ]
