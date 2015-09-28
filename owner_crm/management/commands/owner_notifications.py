# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import car as car_service
from owner_crm.models.renewal import Renewal
from owner_crm.services import owner_emails


class Command(BaseCommand):
    help = 'Sends notifications to owners about the state of their cars'

    def handle(self, *args, **options):
        for car in self._renewable_cars():
            renewal = Renewal.objects.create(car=car)
            owner_emails.renewal_email(car=car, renewal=renewal)

    def _renewable_cars(self):
        # TODO - optimize this query
        oustanding_renewal_cars = [r.car.id for r in Renewal.objects.filter(state=Renewal.STATE_PENDING)]
        return car_service.get_stale_within(
            minutes_until_stale=60 * 2,
        ).exclude(
            id__in = oustanding_renewal_cars,
        )
