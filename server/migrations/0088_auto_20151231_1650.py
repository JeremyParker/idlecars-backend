# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0087_auto_20151230_1845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='service_percentage',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True),
        ),
    ]
