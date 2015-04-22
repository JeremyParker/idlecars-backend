# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0014_auto_20150417_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(to='server.Car')),
                ('user_account', models.OneToOneField(to='server.UserAccount')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
