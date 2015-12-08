# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('server', '0078_auto_20151202_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(help_text='What promotion was this for?', max_length=256, blank=True)),
                ('credit_code', models.CharField(unique=True, max_length=16)),
                ('expiry_time', models.DateTimeField(null=True, blank=True)),
                ('redeem_count', models.IntegerField(default=0, help_text='Number of users who have used this code')),
                ('credit_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('invitor_credit_amount', models.DecimalField(default=0, max_digits=10, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invitor_credited', models.BooleanField(default=False)),
                ('app_credit', models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2)),
                ('invite_code', models.OneToOneField(related_name='invitor', null=True, blank=True, to='server.CreditCode')),
                ('invitor_code', models.ForeignKey(verbose_name='Invited by', blank=True, to='server.CreditCode', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
