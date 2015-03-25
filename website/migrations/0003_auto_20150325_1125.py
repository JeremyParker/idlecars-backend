# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20150324_2014'),
    ]

    operations = [
        migrations.AddField(
            model_name='driversurvey',
            name='driver_prospect',
            field=models.ForeignKey(related_name='driver_survey', to='website.DriverProspect', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ownersurvey',
            name='owner_prospect',
            field=models.ForeignKey(related_name='owner_survey', to='website.OwnerProspect', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driverprospect',
            name='zipcode',
            field=models.CharField(max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip code'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ownerprospect',
            name='zipcode',
            field=models.CharField(max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip code'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)]),
            preserve_default=True,
        ),
    ]
