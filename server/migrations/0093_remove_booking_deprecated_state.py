# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0092_make_model_backfill'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='deprecated_state',
        ),
    ]
