# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from server.services import car as car_service

class Command(BaseCommand):
    help = 'Sends notifications to owners about the state of their cars'

    def handle(self, *args, **options):
        for car in car_service.get_stale_soon():
            self.stdout.write('car {} is about to be delisted.'.format(unicode(car)))
