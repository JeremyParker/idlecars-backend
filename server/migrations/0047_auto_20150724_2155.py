# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0046_auto_20150724_2124'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rideshareprovider',
            old_name='frieldly_id',
            new_name='friendly_id',
        ),
    ]
