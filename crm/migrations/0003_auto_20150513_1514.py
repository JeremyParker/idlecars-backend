# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import crm.models.renewal


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_auto_20150513_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewal',
            name='token',
            field=models.CharField(default=crm.models.renewal._generate_token, max_length=40, db_index=True),
        ),
    ]
