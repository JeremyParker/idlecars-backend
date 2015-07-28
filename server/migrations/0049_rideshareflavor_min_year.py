# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0048_auto_20150727_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='rideshareflavor',
            name='min_year',
            field=models.IntegerField(blank=True, null=True, choices=[(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012'), (2011, '2011'), (2010, '2010'), (2009, '2009'), (2008, '2008'), (2007, '2007'), (2006, '2006'), (2005, '2005'), (2004, '2004'), (2003, '2003'), (2002, '2002'), (2001, '2001'), (2000, '2000'), (1999, '1999'), (1998, '1998'), (1997, '1997'), (1996, '1996')]),
        ),
    ]
