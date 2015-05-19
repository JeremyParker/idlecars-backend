# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0027_auto_20150511_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('user_account', models.OneToOneField(primary_key=True, serialize=False, to='server.UserAccount')),
                ('documentation_complete', models.BooleanField(default=False)),
            ],
        ),
    ]
