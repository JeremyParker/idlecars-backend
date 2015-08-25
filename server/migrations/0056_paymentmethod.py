# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0055_driver_braintree_customer_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gateway_name', models.CharField(max_length=16)),
                ('gateway_token', models.CharField(max_length=256)),
                ('suffix', models.CharField(max_length=4)),
                ('card_type', models.CharField(max_length=32)),
                ('card_logo', models.CharField(max_length=256)),
                ('expiration_date', models.DateField(default=None, null=True, blank=True)),
                ('unique_number_identifier', models.CharField(max_length=32)),
                ('driver', models.ForeignKey(to='server.Driver')),
            ],
        ),
    ]
