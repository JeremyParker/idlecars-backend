# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import owner_crm.models.renewal


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0027_auto_20150511_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Renewal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_time', models.DateTimeField(auto_now=True, null=True)),
                ('state', models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Renewed')])),
                ('token', models.CharField(default=owner_crm.models.consumable_token._generate_token, unique=True, max_length=40, db_index=True)),
                ('car', models.ForeignKey(related_name='renewals', blank=True, to='server.Car', null=True)),
            ],
        ),
    ]
