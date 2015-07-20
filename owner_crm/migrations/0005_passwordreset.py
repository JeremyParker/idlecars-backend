# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import owner_crm.models.consumable_token


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('owner_crm', '0004_auto_20150715_1432'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('state', models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Consumed'), (3, 'Retracted')])),
                ('token', models.CharField(default=owner_crm.models.consumable_token._generate_token, max_length=40, db_index=True)),
                ('auth_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
