# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from django.core.management.base import BaseCommand

from credit.models import Customer
from experiments.models import Experiment, Alternative, Assignment


class Command(BaseCommand):
    def handle(self, *args, **options):
        experiment = Experiment.objects.get_experiment('referral_rewards')
        _50_50 = Alternative.objects.filter(experiment=experiment).exclude(pk=experiment.default.pk)[0]

        for cust in Customer.objects.filter(invite_code__isnull=False):
            print '.'
            if cust.invite_code.credit_amount == decimal.Decimal('75.00'):
                Assignment.objects.create(
                    experiment=experiment,
                    identity=cust.user.username,
                    alternative=experiment.default,
                )
            else:
                Assignment.objects.create(
                    experiment=experiment,
                    identity=cust.user.username,
                    alternative=_50_50,
                )
