# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DriverSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=32, verbose_name='How did you hear about idlecars?')),
                ('other_source', models.CharField(max_length=255, verbose_name='', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OwnerSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=32, verbose_name='How did you hear about idlecars?')),
                ('other_source', models.CharField(max_length=255, verbose_name='', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email Address')),
                ('zipcode', models.CharField(max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip code'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)])),
                ('role', idlecars.model_helpers.ChoiceField(default='Driver', max_length=16, choices=[(b'driver', 'Driver'), (b'owner', 'Owner')])),
                ('created_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='ownersurvey',
            name='contact',
            field=models.ForeignKey(related_name='owner_survey', to='website.Contact', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='contact',
            field=models.ForeignKey(related_name='driver_survey', to='website.Contact', null=True),
            preserve_default=True,
        ),
    ]
