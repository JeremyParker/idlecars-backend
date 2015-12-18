# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0082_auto_20151218_1159'),
    ]

    operations = [
        migrations.RenameField(
            model_name='car',
            old_name='solo_deposit',
            new_name='deposit',
        ),
    ]
