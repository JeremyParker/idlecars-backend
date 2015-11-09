# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0072_auto_20151029_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Missed (Docs)'), (14, 'Missed (CC)'), (2, 'Rejected by Owner'), (3, 'Rejected by Driver'), (4, 'Rented Elsewhere'), (5, 'Test'), (6, 'Driver Canceled'), (7, 'Timed out (Docs)'), (15, 'Timed out (CC)'), (8, 'Timed out Owner/Ins'), (9, 'Insurance rejected: age'), (10, 'Insurance rejected: exp'), (11, 'Insurance rejected: pts'), (12, 'No Base Letter'), (13, 'Other')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Unpaid'), (1, 'Pre-authorized'), (2, 'Paid'), (3, 'In escrow'), (4, 'Refunded'), (5, 'Canceled'), (6, 'Declined'), (7, 'Rejected')]),
        ),
    ]
