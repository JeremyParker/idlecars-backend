# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0079_payment_credit_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='idlecars_supplement',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='payment',
            name='idlecars_transaction_id',
            field=models.CharField(max_length=32, blank=True),
        ),
    ]
