# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
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
        migrations.AlterField(
            model_name='driverprospect',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='Email Address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driverprospect',
            name='zipcode',
            field=models.CharField(max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numbers are allowed in a zip code.', 'Invalid zip code'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ownerprospect',
            name='email',
            field=models.EmailField(unique=True, max_length=254, verbose_name='Email Address'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ownerprospect',
            name='zipcode',
            field=models.CharField(max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]*$', 'Only numbers are allowed in a zip code.', 'Invalid zip code'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)]),
            preserve_default=True,
        ),
    ]
