# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0050_makemodel_passenger_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='merchant_id',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
