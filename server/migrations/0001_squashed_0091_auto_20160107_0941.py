# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from decimal import Decimal
import idlecars.model_helpers
from django.utils.timezone import utc
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    replaces = [('server', '0001_initial'), ('server', '0002_auto_20150326_1214'), ('server', '0003_auto_20150409_1740'), ('server', '0004_auto_20150409_1957'), ('server', '0005_auto_20150410_1718'), ('server', '0006_auto_20150410_2243'), ('server', '0007_car_owner'), ('server', '0008_auto_20150412_1225'), ('server', '0009_auto_20150414_1319'), ('server', '0010_auto_20150414_1348'), ('server', '0011_auto_20150414_1406'), ('server', '0012_auto_20150414_1545'), ('server', '0013_auto_20150415_1422'), ('server', '0014_auto_20150417_1426'), ('server', '0015_booking'), ('server', '0016_auto_20150423_1123'), ('server', '0016_auto_20150423_1331'), ('server', '0017_car_base'), ('server', '0018_auto_20150423_1407'), ('server', '0019_auto_20150424_1217'), ('server', '0020_booking_state'), ('server', '0021_booking_notes'), ('server', '0022_auto_20150430_1709'), ('server', '0023_auto_20150501_1446'), ('server', '0024_auto_20150501_1556'), ('server', '0025_auto_20150508_1352'), ('server', '0026_auto_20150511_1234'), ('server', '0027_auto_20150511_1400'), ('server', '0028_auto_20150607_1354'), ('server', '0030_auto_20150609_1125'), ('server', '0031_auto_20150611_1254'), ('server', '0032_auto_20150610_1201'), ('server', '0033_auto_20150622_1342'), ('server', '0034_auto_20150627_1504'), ('server', '0035_auto_20150628_2049'), ('server', '0037_auto_20150706_1007'), ('server', '0038_driver_notes'), ('server', '0039_makemodel_image_filenames'), ('server', '0041_auto_20150712_1517'), ('server', '0042_auto_20150724_1100'), ('server', '0043_fhvprovider'), ('server', '0044_auto_20150724_2034'), ('server', '0045_rideshareprovider_frieldly_id'), ('server', '0046_auto_20150724_2124'), ('server', '0047_auto_20150724_2155'), ('server', '0048_auto_20150727_1718'), ('server', '0045_auto_20150728_1404'), ('server', '0046_auto_20150729_1656'), ('server', '0049_merge'), ('server', '0050_makemodel_passenger_count'), ('server', '0051_owner_merchant_id'), ('server', '0051_owner_auth_user'), ('server', '0052_merge'), ('server', '0053_auto_20150829_1151'), ('server', '0055_owner_merchant_account_state'), ('server', '0056_driver_braintree_customer_id'), ('server', '0050_auto_20150806_0932'), ('server', '0051_booking_end_time'), ('server', '0052_auto_20150813_1419'), ('server', '0053_auto_20150819_2256'), ('server', '0057_merge'), ('server', '0058_auto_20150914_1734'), ('server', '0059_auto_20150914_2350'), ('server', '0060_payment_service_fee'), ('server', '0061_auto_20150916_1154'), ('server', '0062_payment_created_time'), ('server', '0063_auto_20150917_1449'), ('server', '0064_auto_20150921_1246'), ('server', '0065_auto_20150921_2029'), ('server', '0066_auto_20151002_1436'), ('server', '0067_payment_notes'), ('server', '0067_auto_20151008_1158'), ('server', '0068_merge'), ('server', '0070_auto_20151009_1658'), ('server', '0071_braintreerequest'), ('server', '0072_auto_20151029_1513'), ('server', '0073_auto_20151106_1036'), ('server', '0074_auto_20151123_1609'), ('server', '0075_auto_20151123_2125'), ('server', '0076_auto_20151129_1559'), ('server', '0077_auto_20151130_1909'), ('server', '0078_auto_20151202_1414'), ('server', '0079_payment_credit_amount'), ('server', '0080_auto_20151208_1947'), ('server', '0081_auto_20151214_1020'), ('server', '0082_auto_20151218_1159'), ('server', '0083_auto_20151218_1204'), ('server', '0084_auto_20151218_1214'), ('server', '0085_car_shift'), ('server', '0086_auto_20151218_1302'), ('server', '0087_auto_20151230_1845'), ('server', '0088_auto_20151231_1650'), ('server', '0089_onboardingowner'), ('server', '0089_car_medallion'), ('server', '0090_merge'), ('server', '0091_auto_20160107_0941')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
        ),
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('last_name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
                ('phone_number', models.CharField(max_length=40, blank=True)),
                ('email', models.CharField(blank=True, max_length=128, unique=True, null=True, validators=[django.core.validators.EmailValidator()])),
                ('owner', models.ForeignKey(related_name='user_account', blank=True, to='server.Owner', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='owner',
            field=models.ForeignKey(related_name='cars', blank=True, to='server.Owner', null=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_0_unknown', 'Unknown'), (b'_1_no_min', 'No Minimum'), (b'_2_one_week', 'One Week'), (b'_3_two_weeks', 'Two Weeks'), (b'_4_three_weeks', 'Three Weeks'), (b'_5_one_month', 'One Month'), (b'_6_six_weeks', 'Six Weeks'), (b'_7_two_months', 'Two Months')]),
        ),
        migrations.CreateModel(
            name='MakeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('make', models.CharField(max_length=128, blank=True)),
                ('model', models.CharField(max_length=128, blank=True)),
                ('image_filename', models.CharField(max_length=128, blank=True)),
                ('image_filenames', models.TextField(help_text='Comma separated list of car image filenames. Each name must exist on our Amazon S3 bucket', blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='car',
            name='make',
        ),
        migrations.RemoveField(
            model_name='car',
            name='model',
        ),
        migrations.AddField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(related_name='+', verbose_name='Make & Model', blank=True, to='server.MakeModel', null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='plate',
            field=models.CharField(max_length=24, blank=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(blank=True, max_length=4, null=True, choices=[(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012'), (2011, '2011'), (2010, '2010'), (2009, '2009'), (2008, '2008'), (2007, '2007'), (2006, '2006'), (2005, '2005'), (2004, '2004'), (2003, '2003'), (2002, '2002'), (2001, '2001'), (2000, '2000'), (1999, '1999'), (1998, '1998'), (1997, '1997'), (1996, '1996')]),
        ),
        migrations.RenameField(
            model_name='car',
            old_name='status_date',
            new_name='next_available_date',
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_0_unknown', 'Unknown'), (b'_1_no_min', 'No'), (b'_2_one_week', 'One Week'), (b'_3_two_weeks', 'Two Weeks'), (b'_4_three_weeks', 'Three Weeks'), (b'_5_one_month', 'One Month'), (b'_6_six_weeks', 'Six Weeks'), (b'_7_two_months', 'Two Months')]),
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='No Minimum', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', 'One Week'), (b'_03_two_weeks', 'Two Weeks'), (b'_04_three_weeks', 'Three Weeks'), (b'_05_one_month', 'One Month'), (b'_06_six_weeks', 'Six Weeks'), (b'_07_two_months', 'Two Months'), (b'_08_three_months', 'Three Months'), (b'_09_four_months', 'Four Months'), (b'_10_five_months', 'Five Months'), (b'_11_six_months', 'Six Months')]),
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('car', models.ForeignKey(to='server.Car')),
                ('user_account', models.ForeignKey(to='server.UserAccount', null=True)),
                ('state', models.IntegerField(default=1, choices=[(1, 'Pending - waiting for driver docs'), (2, 'Complete - checking driver creds'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, 'Flake - Never Submitted Docs'), (7, 'Too Slow - driver took too long to submit docs'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver'), (11, 'Test - a booking that one of us created as a test')])),
                ('notes', models.TextField(blank=True)),
            ],
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default=b'_07_two_months', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', 'One Week'), (b'_03_two_weeks', 'Two Weeks'), (b'_04_three_weeks', 'Three Weeks'), (b'_05_one_month', 'One Month'), (b'_06_six_weeks', 'Six Weeks'), (b'_07_two_months', 'Two Months'), (b'_08_three_months', 'Three Months'), (b'_09_four_months', 'Four Months'), (b'_10_five_months', 'Five Months'), (b'_11_six_months', 'Six Months')]),
        ),
        migrations.AddField(
            model_name='car',
            name='hybrid',
            field=models.BooleanField(default=False, verbose_name='This car is a hybrid'),
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default=b'_07_two_months', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', 'One Week'), (b'_03_two_weeks', 'Two Weeks'), (b'_04_three_weeks', 'Three Weeks'), (b'_05_one_month', 'One Month'), (b'_06_six_weeks', 'Six Weeks'), (b'_07_two_months', 'Two Months'), (b'_08_three_months', 'Three Months'), (b'_09_four_months', 'Four Months'), (b'_10_five_months', 'Five Months'), (b'_11_six_months', 'Six Months')]),
        ),
        migrations.AddField(
            model_name='car',
            name='base',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.RenameField(
            model_name='car',
            old_name='solo_cost',
            new_name='weekly_rent',
        ),
        migrations.AlterField(
            model_name='car',
            name='weekly_rent',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
        ),
        migrations.RenameField(
            model_name='car',
            old_name='solo_deposit',
            new_name='deposit',
        ),
        migrations.AlterField(
            model_name='car',
            name='deposit',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=0, blank=True),
        ),
        migrations.RemoveField(
            model_name='car',
            name='split_cost',
        ),
        migrations.RemoveField(
            model_name='car',
            name='split_deposit',
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='_00_unknown', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', 'One Week'), (b'_03_two_weeks', 'Two Weeks'), (b'_04_three_weeks', 'Three Weeks'), (b'_05_one_month', 'One Month'), (b'_06_six_weeks', 'Six Weeks'), (b'_07_two_months', 'Two Months'), (b'_08_three_months', 'Three Months'), (b'_09_four_months', 'Four Months'), (b'_10_five_months', 'Five Months'), (b'_11_six_months', 'Six Months')]),
        ),
        migrations.AddField(
            model_name='car',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='created_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(blank=True, null=True, choices=[(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012'), (2011, '2011'), (2010, '2010'), (2009, '2009'), (2008, '2008'), (2007, '2007'), (2006, '2006'), (2005, '2005'), (2004, '2004'), (2003, '2003'), (2002, '2002'), (2001, '2001'), (2000, '2000'), (1999, '1999'), (1998, '1998'), (1997, '1997'), (1996, '1996')]),
        ),
        migrations.RemoveField(
            model_name='owner',
            name='last_engagement',
        ),
        migrations.AddField(
            model_name='car',
            name='last_status_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address_proof_image', idlecars.model_helpers.StrippedCharField(max_length=300, blank=True)),
                ('defensive_cert_image', idlecars.model_helpers.StrippedCharField(max_length=300, blank=True)),
                ('driver_license_image', idlecars.model_helpers.StrippedCharField(max_length=300, blank=True)),
                ('fhv_license_image', idlecars.model_helpers.StrippedCharField(max_length=300, blank=True)),
                ('auth_user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL)),
                ('documentation_approved', models.BooleanField(default=False, verbose_name='docs approved', db_column='documentation_complete')),
                ('notes', models.TextField(blank=True)),
                ('braintree_customer_id', models.CharField(max_length=32, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='booking',
            name='driver',
            field=models.ForeignKey(to='server.Driver', null=True),
        ),
        migrations.AddField(
            model_name='useraccount',
            name='driver',
            field=models.OneToOneField(related_name='user_account', null=True, blank=True, to='server.Driver'),
        ),
        migrations.CreateModel(
            name='Insurance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insurer_name', models.CharField(max_length=256, blank=True)),
                ('insurance_code', models.CharField(max_length=8, unique=True, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='exterior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan'), (6, 'White')]),
        ),
        migrations.AddField(
            model_name='car',
            name='interior_color',
            field=models.IntegerField(blank=True, null=True, choices=[(0, 'Black'), (1, 'Charcoal'), (2, 'Grey'), (3, 'Dark Blue'), (4, 'Blue'), (5, 'Tan'), (6, 'White')]),
        ),
        migrations.AddField(
            model_name='car',
            name='last_known_mileage',
            field=models.CommaSeparatedIntegerField(max_length=32, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='last_mileage_update',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='insurance',
            field=models.ForeignKey(blank=True, to='server.Insurance', null=True),
        ),
        migrations.RenameField(
            model_name='booking',
            old_name='state',
            new_name='deprecated_state',
        ),
        migrations.AlterField(
            model_name='booking',
            name='deprecated_state',
            field=models.IntegerField(default=1, choices=[(1, 'Pending - waiting for driver docs'), (2, 'Complete - checking driver creds'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, "Flake - Didn't Submit Docs in 24 hours"), (7, 'Too Slow - somebody else booked your car'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver'), (11, 'Test - a booking that one of us created as a test'), (12, 'Canceled - driver canceled the booking thru the app')]),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.CharField(blank=True, max_length=128, null=True, validators=[django.core.validators.EmailValidator()]),
        ),
        migrations.AlterField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(default=1, verbose_name='Make & Model', to='server.MakeModel'),
        ),
        migrations.AlterField(
            model_name='car',
            name='min_lease',
            field=idlecars.model_helpers.ChoiceField(default='_00_unknown', max_length=32, choices=[(b'_00_unknown', 'Unknown'), (b'_01_no_min', 'No'), (b'_02_one_week', '7 days'), (b'_03_two_weeks', '14 days'), (b'_04_three_weeks', '21 days'), (b'_05_one_month', '30 days'), (b'_06_six_weeks', '45 days'), (b'_07_two_months', '60 days'), (b'_08_three_months', '90 days'), (b'_09_four_months', '120 days'), (b'_10_five_months', '150 days'), (b'_11_six_months', '180 days')]),
        ),
        migrations.CreateModel(
            name='RideshareFlavor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('friendly_id', models.CharField(unique=True, max_length=32)),
                ('compatible_models', models.ManyToManyField(to=b'server.MakeModel')),
            ],
        ),
        migrations.AddField(
            model_name='makemodel',
            name='body_type',
            field=models.IntegerField(default=0, choices=[(0, 'Sedan'), (1, 'SUV')]),
        ),
        migrations.AddField(
            model_name='makemodel',
            name='lux_level',
            field=models.IntegerField(default=0, choices=[(0, 'Standard'), (1, 'Luxury')]),
        ),
        migrations.AddField(
            model_name='makemodel',
            name='passenger_count',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='merchant_id',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='auth_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='owner',
            name='merchant_account_state',
            field=models.IntegerField(null=True, choices=[(1, 'Pending'), (2, 'Approved'), (3, 'Declined')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='approval_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='return_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='checkout_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_reason',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Missed (Docs)'), (14, 'Missed (CC)'), (2, 'Rejected by Owner'), (3, 'Rejected by Driver'), (4, 'Rented Elsewhere'), (5, 'Test'), (6, 'Driver Canceled'), (7, 'Timed out (Docs)'), (15, 'Timed out (CC)'), (8, 'Timed out Owner/Ins'), (9, 'Insurance rejected: age'), (10, 'Insurance rejected: exp'), (11, 'Insurance rejected: pts'), (12, 'No Base Letter'), (13, 'Other')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='incomplete_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='pickup_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='refund_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='requested_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('status', models.IntegerField(default=0, choices=[(0, 'Pending gateway response'), (1, 'Payment approved'), (2, 'Payment declined'), (3, 'Card rejected')])),
                ('error_message', models.CharField(max_length=256)),
                ('transaction_id', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('gateway_token', models.CharField(max_length=256)),
                ('suffix', models.CharField(max_length=4)),
                ('card_type', models.CharField(max_length=32)),
                ('card_logo', models.CharField(max_length=256)),
                ('expiration_date', models.DateField(default=None, null=True, blank=True)),
                ('unique_number_identifier', models.CharField(max_length=32)),
                ('driver', models.ForeignKey(to='server.Driver')),
            ],
        ),
        migrations.AlterField(
            model_name='booking',
            name='deprecated_state',
            field=models.IntegerField(default=0, choices=[(0, 'State comes from event times, not from this field.'), (1, 'Pending - waiting for driver docs'), (2, 'Complete - driver uploaded all docs'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, "Flake - Didn't Submit Docs in 24 hours"), (7, 'Too Slow - somebody else booked your car'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver'), (11, 'Test - a booking that one of us created as a test'), (12, 'Canceled - driver canceled the booking thru the app')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='booking',
            field=models.ForeignKey(to='server.Booking'),
        ),
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.ForeignKey(blank=True, to='server.PaymentMethod', null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Pre-authorized'), (3, 'In Escrow'), (4, 'Voided'), (5, 'Payment declined'), (6, 'Card rejected')]),
        ),
        migrations.AlterField(
            model_name='payment',
            name='transaction_id',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='service_fee',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Pre-authorized'), (3, 'In Escrow'), (4, 'Payment refunded'), (5, 'Voided'), (6, 'Payment declined'), (7, 'Card rejected')]),
        ),
        migrations.AddField(
            model_name='payment',
            name='created_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 16, 19, 58, 38, 790353, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice_start_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Pending'), (1, 'Pre-authorized'), (2, 'Settled'), (3, 'In Escrow'), (4, 'Payment refunded'), (5, 'Voided'), (6, 'Payment declined'), (7, 'Card rejected')]),
        ),
        migrations.AddField(
            model_name='booking',
            name='service_percentage',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='weekly_rent',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='service_percentage',
            field=models.DecimalField(null=True, verbose_name='Negotiated service percentage', max_digits=10, decimal_places=4, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='base_letter',
            field=idlecars.model_helpers.StrippedCharField(max_length=300, blank=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='base_letter_rejected',
            field=models.BooleanField(default=False, verbose_name='base letter rejected'),
        ),
        migrations.AddField(
            model_name='payment',
            name='notes',
            field=models.TextField(blank=True),
        ),
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
        migrations.AddField(
            model_name='driver',
            name='sms_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='owner',
            name='sms_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'Unpaid'), (1, 'Pre-authorized'), (2, 'Paid'), (3, 'In escrow'), (4, 'Refunded'), (5, 'Canceled'), (6, 'Declined'), (7, 'Rejected')]),
        ),
        migrations.AddField(
            model_name='car',
            name='active_in_tlc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='car',
            name='base_address',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_number',
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_telephone_number',
            field=models.CharField(max_length=16, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='base_type',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'Livery'), (2, 'Paratrans')]),
        ),
        migrations.AddField(
            model_name='car',
            name='expiration_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='found_in_tlc',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='car',
            name='last_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='car',
            name='registrant_name',
            field=models.CharField(max_length=64, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='vehicle_vin_number',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='insurance_policy_number',
            field=models.CharField(max_length=32, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='car',
            name='next_available_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='credit_amount',
            field=models.DecimalField(default=Decimal('0.00'), verbose_name='Credit', max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='payment',
            name='idlecars_supplement',
            field=models.DecimalField(default=Decimal('0.00'), max_digits=10, decimal_places=2),
        ),
        migrations.AddField(
            model_name='payment',
            name='idlecars_transaction_id',
            field=models.CharField(max_length=32, blank=True),
        ),
        migrations.AddField(
            model_name='car',
            name='shift',
            field=models.IntegerField(default=0, choices=[(0, 'Unknown'), (1, '24/7'), (2, 'Day shift (5am-5pm)'), (3, 'Night shift (5pm-5am)')]),
        ),
        migrations.CreateModel(
            name='OnboardingOwner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('published_date', models.DateTimeField(null=True, blank=True)),
                ('phone_number', models.CharField(unique=True, max_length=40)),
                ('name', idlecars.model_helpers.StrippedCharField(max_length=30, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='car',
            name='medallion',
            field=models.BooleanField(default=False),
        ),
    ]
