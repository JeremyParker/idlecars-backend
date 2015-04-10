# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_auto_20150409_1740'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='User',
            new_name='UserAccount',
        ),
    ]
