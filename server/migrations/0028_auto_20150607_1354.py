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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('documentation_complete', models.BooleanField(default=False, verbose_name='docs confirmed')),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='user_account',
            field=models.ForeignKey(to='server.UserAccount', null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='driver',
            field=models.ForeignKey(to='server.Driver', null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='driver',
            field=models.OneToOneField(null=True, to='server.Driver'),
        ),
    ]
