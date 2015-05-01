# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0023_auto_20150501_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='user_account',
            field=models.ForeignKey(to='server.UserAccount'),
        ),
    ]
