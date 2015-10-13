# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0062_payment_created_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='week_ending',
            new_name='invoice_end_time',
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Settled'), (3, 'In Escrow'), (4, 'Payment refunded'), (5, 'Voided'), (6, 'Payment declined'), (7, 'Card rejected')]),
        ),
    ]
