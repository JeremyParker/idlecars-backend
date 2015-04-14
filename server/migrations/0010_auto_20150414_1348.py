# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0009_auto_20150414_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='car',
            name='plate',
            field=models.CharField(max_length=24, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='make_model',
            field=models.ForeignKey(related_name='+', verbose_name='Make & Model', blank=True, to='server.MakeModel', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='car',
            name='year',
            field=models.IntegerField(blank=True, max_length=4, null=True, choices=[(2016, '2016'), (2015, '2015'), (2014, '2014'), (2013, '2013'), (2012, '2012'), (2011, '2011'), (2010, '2010'), (2009, '2009'), (2008, '2008'), (2007, '2007'), (2006, '2006'), (2005, '2005'), (2004, '2004'), (2003, '2003'), (2002, '2002'), (2001, '2001'), (2000, '2000'), (1999, '1999'), (1998, '1998'), (1997, '1997'), (1996, '1996')]),
            preserve_default=True,
        ),
    ]
