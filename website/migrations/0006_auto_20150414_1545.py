# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0005_auto_20150330_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='role',
            field=idlecars.model_helpers.ChoiceField(default='driver', max_length=16, choices=[(b'driver', ''), (b'owner', '')]),
            preserve_default=True,
        ),
    ]
