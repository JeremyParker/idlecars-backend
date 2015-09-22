# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0063_auto_20150917_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='service_percentage',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=4),
        ),
        migrations.AddField(
            model_name='booking',
            name='weekly_rent',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='owner',
            name='service_percentage',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=4),
        ),
    ]
