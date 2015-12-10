# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0078_auto_20151202_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='credit_amount',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
    ]
