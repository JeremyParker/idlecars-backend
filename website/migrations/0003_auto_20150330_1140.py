# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20150327_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='role',
            field=idlecars.model_helpers.ChoiceField(default='Driver', max_length=16, choices=[(b'driver', 'I want to drive.'), (b'owner', 'I own a car.')]),
            preserve_default=True,
        ),
    ]
