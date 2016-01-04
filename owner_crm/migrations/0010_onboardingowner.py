# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0009_auto_20151204_1542'),
    ]

    operations = [
        migrations.CreateModel(
            name='OnboardingOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('published_date', models.DateTimeField(null=True, blank=True)),
                ('phone_number', models.CharField(unique=True, max_length=40)),
                ('name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
            ],
        ),
    ]
