# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0053_auto_20150819_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='owner',
            name='merchant_id',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
