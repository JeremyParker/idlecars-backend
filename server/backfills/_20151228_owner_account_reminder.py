# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.utils import timezone

from server.models import Owner
from server.services import owner_service

from owner_crm.services import throttle_service

def run_backfill():
    '''
    mark throttle system the existing owners who signed up 47 hours ago FirstSignupReminder so that
    they don't get two reminders at the same time when we launch
    '''
    campaign = 'FirstAccountReminder'
    backfill_owners = owner_service.filter_incomplete(Owner.objects.all()).filter(
        auth_users__date_joined__lte=timezone.now() - datetime.timedelta(hours=47),
        cars__isnull=False,
    )
    throttle_service.mark_sent(throttle_service.throttle(backfill_owners, campaign), campaign)
