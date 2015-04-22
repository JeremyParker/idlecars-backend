# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0002_auto_20150326_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', idlecars.model_helpers.ChoiceField(default='Unknown', max_length=32, choices=[(b'available', 'Available'), (b'busy', 'Busy'), (b'unknown', 'Unknown')])),
                ('status_date', models.DateField(null=True, blank=True)),
                ('make', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
                ('year', models.IntegerField(blank=True, max_length=4, null=True, choices=[(1995, '1995'), (1996, '1996'), (1997, '1997'), (1998, '1998'), (1999, '1999'), (2000, '2000'), (2001, '2001'), (2002, '2002'), (2003, '2003'), (2004, '2004'), (2005, '2005'), (2006, '2006'), (2007, '2007'), (2008, '2008'), (2009, '2009'), (2010, '2010'), (2011, '2011'), (2012, '2012'), (2013, '2013'), (2014, '2014'), (2015, '2015')])),
                ('solo_cost', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('solo_deposit', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('split_cost', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('split_deposit', models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True)),
                ('min_lease', idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_0_no_min', 'No Minimum'), (b'_1_one_week', 'One Week'), (b'_2_two_weeks', 'Two Weeks'), (b'_3_three_weeks', 'Three Weeks'), (b'_4_one_month', 'One Month'), (b'_5_six_weeks', 'Six Weeks'), (b'_6_two_months', 'Two Months')])),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=256, blank=True)),
                ('address1', models.CharField(max_length=200, blank=True)),
                ('address2', models.CharField(max_length=200, blank=True)),
                ('city', models.CharField(max_length=200, blank=True)),
                ('state_code', models.CharField(max_length=2, blank=True)),
                ('zipcode', models.CharField(blank=True, max_length=5, verbose_name='Zip Code', validators=[django.core.validators.RegexValidator('^[0-9]+$', 'Only numbers are allowed in a zip code.', 'Invalid zip'), django.core.validators.MinLengthValidator(5), django.core.validators.MaxLengthValidator(5)])),
                ('split_shift', models.NullBooleanField(verbose_name='Accepts Split Shifts')),
                ('rating', models.IntegerField(blank=True, help_text="Owner's rating based on previous experience.", null=True, choices=[(0, 'Terrible'), (1, 'Bad'), (2, 'Poor'), (3, 'OK'), (4, 'Good'), (5, 'Excellent')])),
                ('last_engagement', models.DateField(null=True, blank=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('last_name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('phone_number', models.CharField(max_length=40, blank=True)),
                ('email', models.CharField(max_length=128, unique=True, null=True, blank=True)),
                ('owner', models.ForeignKey(related_name='contacts', blank=True, to='server.Owner', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Driver',
        ),
        migrations.DeleteModel(
            name='FleetPartner',
        ),
    ]
