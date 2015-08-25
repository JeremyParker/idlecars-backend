# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0054_auto_20150824_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='braintree_customer_id',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
    ]
