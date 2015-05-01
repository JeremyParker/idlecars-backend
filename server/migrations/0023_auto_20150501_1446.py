# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0022_auto_20150430_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='state',
            field=models.IntegerField(default=1, choices=[(1, 'Pending - waiting for driver docs'), (2, 'Complete - checking driver creds'), (3, 'Requested - waiting for owner/insurance'), (4, 'Accepted - waiting for deposit, ssn, contract'), (5, 'Booked - car marked busy with new available_time'), (6, 'Flake - Never Submitted Docs'), (7, 'Too Slow - driver took too long to submit docs'), (8, 'Owner Rejected - driver wasn\t approved'), (9, 'Driver Rejected - driver changed their mind'), (10, 'Missed - car rented out before we found a driver')]),
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(blank=True, null=True, choices=[(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012'), (2011, '2011'), (2010, '2010'), (2009, '2009'), (2008, '2008'), (2007, '2007'), (2006, '2006'), (2005, '2005'), (2004, '2004'), (2003, '2003'), (2002, '2002'), (2001, '2001'), (2000, '2000'), (1999, '1999'), (1998, '1998'), (1997, '1997'), (1996, '1996')]),
        ),
    ]
