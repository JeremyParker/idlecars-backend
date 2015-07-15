# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0003_auto_20150513_1514'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewal',
            name='state',
            field=models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Consumed'), (3, 'Retracted')]),
        ),
    ]
