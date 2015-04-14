# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0010_auto_20150414_1348'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='status_date',
            new_name='next_available_date',
        ),
    ]
