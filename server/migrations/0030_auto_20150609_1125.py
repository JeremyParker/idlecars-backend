# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0029_20150708_backfill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='driver',
            field=models.OneToOneField(related_name='user_account', null=True, blank=True, to='server.Driver'),
        ),
    ]
