# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0064_auto_20150921_1246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paymentmethod',
            name='gateway_name',
        ),
        migrations.AlterField(
            model_name='owner',
            name='service_percentage',
            field=models.DecimalField(null=True, verbose_name='Negotiated service percentage', max_digits=10, decimal_places=4),
        ),
    ]
