# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idlecars.model_helpers
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='driversurvey',
            name='account_gett',
            field=models.BooleanField(default=False, verbose_name='Gett'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_lyft',
            field=models.BooleanField(default=False, verbose_name='Lyft'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_other',
            field=models.BooleanField(default=False, verbose_name='Other Dispatcher'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_other_name',
            field=models.CharField(max_length=255, verbose_name='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_uber',
            field=models.BooleanField(default=False, verbose_name='Uber'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_via',
            field=models.BooleanField(default=False, verbose_name='Via'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='account_whisk',
            field=models.BooleanField(default=False, verbose_name='Whisk'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='car_owner',
            field=models.BooleanField(default=False, verbose_name='I own a car'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='credit_card',
            field=models.BooleanField(default=False, verbose_name='I have a credit card'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_friday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_monday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_saturday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_sunday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_thursday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_tuesday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='end_wednesday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='exchange',
            field=idlecars.model_helpers.ChoiceField(default='No response', max_length=256, verbose_name='', choices=[(b'_no_response', 'No response'), (b'delivery', 'I would need the vehicle delivered to my home at the start of every shift'), (b'garage', 'I can pick up the vehicle from a parking garage at the start of every shift.'), (b'overnight', 'I would need to keep the vehicle in my posession between shifts')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='licenced',
            field=models.BooleanField(default=False, verbose_name="I have a commercial driver's license"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_friday',
            field=models.BooleanField(default=False, verbose_name='Friday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_monday',
            field=models.BooleanField(default=False, verbose_name='Monday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_saturday',
            field=models.BooleanField(default=False, verbose_name='Saturday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_sunday',
            field=models.BooleanField(default=False, verbose_name='Sunday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_thursday',
            field=models.BooleanField(default=False, verbose_name='Thursday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_tuesday',
            field=models.BooleanField(default=False, verbose_name='Tuesday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='rent_wednesday',
            field=models.BooleanField(default=False, verbose_name='Wednesday'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_friday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_monday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_saturday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_sunday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_thursday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_tuesday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='start_wednesday',
            field=models.TimeField(default=datetime.time(0, 0), verbose_name=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='driversurvey',
            name='vehicle_type',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=64, verbose_name='What kind of vehicle would you prefer to rent?', choices=[(b'sedan', 'Luxury Sedan'), (b'suv', 'Luxury SUV'), (b'uber_x', 'Any Vehicle')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driversurvey',
            name='source',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=32, verbose_name='How did you hear about idlecars?', choices=[(b'_2_mouth', 'Word of mouth'), (b'_3_poster', 'I saw a poster'), (b'_4_search', 'I searched online'), (b'_5_facebook', 'Facebook'), (b'_6_twitter', 'Twitter'), (b'_7_other', 'Other')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ownersurvey',
            name='source',
            field=idlecars.model_helpers.ChoiceField(blank=True, max_length=32, verbose_name='How did you hear about idlecars?', choices=[(b'_2_mouth', 'Word of mouth'), (b'_3_poster', 'I saw a poster'), (b'_4_search', 'I searched online'), (b'_5_facebook', 'Facebook'), (b'_6_twitter', 'Twitter'), (b'_7_other', 'Other')]),
            preserve_default=True,
        ),
    ]
