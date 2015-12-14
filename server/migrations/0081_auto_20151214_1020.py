# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0080_auto_20151208_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='credit_amount',
            field=models.DecimalField(default=Decimal('0.00'), verbose_name='Credit', max_digits=10, decimal_places=2),
        ),
    ]
