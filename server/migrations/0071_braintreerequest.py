# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0070_auto_20151009_1658'),
    ]

    operations = [
        migrations.CreateModel(
            name='BraintreeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('endpoint', models.CharField(max_length=64)),
                ('request', models.TextField(blank=True)),
                ('response', models.TextField(blank=True)),
                ('payment', models.ForeignKey(to='server.Payment', null=True)),
                ('payment_method', models.ForeignKey(to='server.PaymentMethod', null=True)),
            ],
        ),
    ]
