# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0056_paymentmethod'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='gateway_token',
            new_name='transaction_id',
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.ForeignKey(blank=True, to='server.PaymentMethod', null=True),
        ),
    ]
