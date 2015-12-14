# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0008_auto_20151112_1037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='renewal',
            name='car',
        ),
        migrations.DeleteModel(
            name='Renewal',
        ),
    ]
