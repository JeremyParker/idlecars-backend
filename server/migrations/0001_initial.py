# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import server.model_helpers


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', server.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('last_name', server.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('phone_number', models.CharField(max_length=40, blank=True)),
                ('email', models.CharField(max_length=128, unique=True, null=True, blank=True)),
                ('email_verified', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FleetPartner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('contact', models.CharField(max_length=256, blank=True)),
                ('phone', models.CharField(help_text=b'Comma separated', max_length=256, blank=True)),
                ('email', models.CharField(help_text=b'Comma separated', max_length=256, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
