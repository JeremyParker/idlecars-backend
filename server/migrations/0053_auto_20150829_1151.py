# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0052_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='owner',
            old_name='auth_user',
            new_name='auth_users',
        ),
    ]
