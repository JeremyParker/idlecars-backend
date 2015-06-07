# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backfill_drivers(apps, schema_editor):
    '''
    associate a (new) driver object for all bookings
    '''
    Booking = apps.get_model("server", "Booking")
    Driver = apps.get_model("server", "Driver")

    for booking in Booking.objects.all():
        if Driver.objects.filter(user_account=booking.user_account).exists():
            booking.driver = Driver.objects.get(user_account=booking.user_account)
        else:
            new_driver = Driver.objects.create()
            booking.user_account.driver = new_driver
            booking.user_account.save()
            booking.driver = new_driver
        booking.save()
        print('.')


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0028_auto_20150607_1354'),
    ]

    operations = [
        migrations.RunPython(backfill_drivers),
    ]
