# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20150409_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.CharField(default='', unique=True, max_length=128, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='owner',
            field=models.ForeignKey(related_name='user_account', blank=True, to='server.Owner', null=True),
            preserve_default=True,
        ),
    ]
