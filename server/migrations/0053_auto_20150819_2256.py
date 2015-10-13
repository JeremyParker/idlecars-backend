# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0052_auto_20150813_1419'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='state',
            new_name='deprecated_state',
        ),
    ]
