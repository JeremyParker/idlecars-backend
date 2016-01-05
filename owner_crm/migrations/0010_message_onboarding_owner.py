# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0089_onboardingowner'),
        ('owner_crm', '0009_auto_20151204_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='onboarding_owner',
            field=models.ForeignKey(blank=True, to='server.OnboardingOwner', null=True),
        ),
    ]
