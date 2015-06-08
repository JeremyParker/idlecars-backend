# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def backfill_drivers(apps, schema_editor):
    '''
    associate a (new) driver object for all bookings
    '''
    Booking = apps.get_model("server", "Booking")
    Driver = apps.get_model("server", "Driver")
    UserAccount = apps.get_model("server", "UserAccount")

    import pdb; pdb.set_trace()
    for booking in Booking.objects.all():
        user_account = UserAccount.objects.get(pk=booking.user_account.pk)
        if user_account.driver:
            booking.driver = user_account.driver
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
