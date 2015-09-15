# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0059_auto_20150914_2350'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='service_fee',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
    ]
