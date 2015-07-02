# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def flakes_are_too_slow(apps, schema_editor):
    '''
    change all FLAKE bookings to TOO_SLOW
    '''
    Booking = apps.get_model("server", "Booking")
    FLAKE = 6
    TOO_SLOW = 7

    for booking in Booking.objects.filter(state=FLAKE):
        booking.state = TOO_SLOW
        booking.save()
        print('.')


class Migration(migrations.Migration):
    dependencies = [
        ('server', '0035_auto_20150628_2049'),
    ]

    operations = [
        migrations.RunPython(flakes_are_too_slow),
    ]
