# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import owner_crm.models.renewal


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0002_auto_20150513_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewal',
            name='token',
            field=models.CharField(default=owner_crm.models.renewal._generate_token, max_length=40, db_index=True),
        ),
    ]
