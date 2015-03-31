# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_auto_20150330_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='driversurvey',
            old_name='end_friday',
            new_name='shift_other_end',
        ),
        migrations.RenameField(
            model_name='driversurvey',
            old_name='end_monday',
            new_name='shift_other_start',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='end_saturday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='end_sunday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='end_thursday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='end_tuesday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='end_wednesday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_friday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_monday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_saturday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_sunday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_thursday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_tuesday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='rent_wednesday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_friday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_monday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_saturday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_sunday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_thursday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_tuesday',
        ),
        migrations.RemoveField(
            model_name='driversurvey',
            name='start_wednesday',
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_groundlink',
            field=models.BooleanField(default=False, verbose_name='Groundlink'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='shift_choice',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=128, verbose_name='What shift would you prefer to drive?', choices=[(b'_1', '4am to 3pm'), (b'_2', '4pm to 3am'), (b'other', 'Something else')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contact',
            name='role',
            field=idlecars.model_helpers.ChoiceField(default='driver', max_length=16, choices=[(b'driver', 'I want to drive.'), (b'owner', 'I own a car.')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driversurvey',
            name='car_owner',
            field=models.BooleanField(default=False, verbose_name="I don't own a car"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driversurvey',
            name='source',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=32, verbose_name='How did you hear about idlecars?', choices=[(b'_1_idlecars', 'From someone at idlecars'), (b'_2_mouth', 'From a friend'), (b'_3_poster', 'I saw a poster'), (b'_4_search', 'I searched online'), (b'_5_facebook', 'Facebook'), (b'_6_twitter', 'Twitter'), (b'_7_other', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driversurvey',
            name='vehicle_type',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=64, verbose_name='What kind of vehicle would you prefer to rent?', choices=[(b'luxury_sedan', 'Luxury Sedan'), (b'luxury_suv', 'Luxury SUV'), (b'sedan', 'Non-luxury Sedan or Crossover'), (b'suv', 'Non-luxury SUV and MiniVan')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ownersurvey',
            name='source',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=32, verbose_name='How did you hear about idlecars?', choices=[(b'_1_idlecars', 'From someone at idlecars'), (b'_2_mouth', 'From a friend'), (b'_3_poster', 'I saw a poster'), (b'_4_search', 'I searched online'), (b'_5_facebook', 'Facebook'), (b'_6_twitter', 'Twitter'), (b'_7_other', 'Other')]),
            preserve_default=True,
        ),
    ]
