# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0056_driver_braintree_customer_id'),
        ('owner_crm', '0005_passwordreset'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.CharField(max_length=255)),
                ('booking', models.ForeignKey(blank=True, to='server.Booking', null=True)),
                ('car', models.ForeignKey(blank=True, to='server.Car', null=True)),
                ('driver', models.ForeignKey(blank=True, to='server.Driver', null=True)),
                ('owner', models.ForeignKey(blank=True, to='server.Owner', null=True)),
            ],
        ),
    ]
