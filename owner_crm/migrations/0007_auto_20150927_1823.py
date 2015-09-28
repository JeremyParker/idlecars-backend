# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('owner_crm', '0006_message'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTopic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='message',
            name='booking',
        ),
        migrations.RemoveField(
            model_name='message',
            name='car',
        ),
        migrations.RemoveField(
            model_name='message',
            name='driver',
        ),
        migrations.RemoveField(
            model_name='message',
            name='owner',
        ),
        migrations.AddField(
            model_name='message',
            name='message_topic',
            field=models.ForeignKey(to='owner_crm.MessageTopic', null=True),
        ),
    ]
