# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from factory import LazyAttribute

from idlecars.factory_helpers import Factory
from owner_crm import models


class Campaign(Factory):
    class Meta:
        model = 'owner_crm.Campaign'

    name = LazyAttribute(lambda o: 'fake name')
    preferred_medium = LazyAttribute(
      lambda o: randon.choice([models.Campaign.SMS_MEDIUM, models.Campaign.EMAIL_MEDIUM])
    )


class SmsCampaign(Campaign):
    preferred_medium = models.Campaign.SMS_MEDIUM


class EmailCampaign(Campaign):
    preferred_medium = models.Campaign.EMAIL_MEDIUM
