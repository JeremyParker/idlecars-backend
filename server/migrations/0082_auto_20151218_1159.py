# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0081_auto_20151214_1020'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='solo_cost',
            new_name='weekly_rent',
        ),
    ]
