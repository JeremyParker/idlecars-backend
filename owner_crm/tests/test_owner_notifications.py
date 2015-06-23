# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import mock

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import idlecars.client_side_routes
import server.models
import owner_crm.models
import server.factories
import owner_crm.factories
from owner_crm.management.commands import owner_notifications
from owner_crm.tests import sample_merge_vars


class TestOwnerNotifications(TestCase):
    def _setup_car_with_update_time(self, update_time):
        owner = server.factories.Owner.create()
        car = server.factories.BookableCar.create(
            last_status_update=update_time,
            owner=owner,
        )
        server.factories.UserAccount.create(owner=owner)
        return car

    def _update_time_about_to_go_stale(self):
        # TODO - get the stale_threshold from config
        return timezone.now() - datetime.timedelta(days=3, hours=23, minutes=50)

    def test_whole_enchilada(self):
        last_update = self._update_time_about_to_go_stale()

        cars = []
        for i in xrange(2):  # two cars about to go stale
            cars.append(self._setup_car_with_update_time(last_update))

        # one car just renewed to make sure filtering is working
        self._setup_car_with_update_time(timezone.now())

        call_command('owner_notifications')

        # check what got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        subjects = [m.subject for m in outbox]
        for car in cars:
            self.assertTrue('Your {} listing is about to expire.'.format(car.__unicode__()) in subjects)

        template_dict = owner_crm.tests.sample_merge_vars.merge_vars[outbox[0].template_name]
        expected_keys = set(template_dict.values()[0])

        # validate that the merge vars are being set correctly:
        for message in outbox:
            email = message.merge_vars.keys()[0]
            user = server.models.UserAccount.objects.get(email=email)
            car =server.models.Owner.objects.get(user_account=user).cars.all()[0]
            renewal = owner_crm.models.Renewal.objects.get(car=car)
            var = message.merge_vars[email]

            self.assertEqual(var['CTA_LABEL'], 'Renew Listing Now')
            self.assertEqual(var['CTA_URL'], idlecars.client_side_routes.renewal_url(renewal))
            self.assertEqual(var['FNAME'], user.first_name)
            self.assertTrue(car.plate in var['TEXT'])
            self.assertTrue(car.__unicode__() in var['TEXT'])

            # Make sure the merge vars are the ones we're testing against in the integration test
            self.assertEqual(set([]), set(var.keys()) - expected_keys)


    def test_notifiable_cars(self):
        '''
        Make sure cars that have an outstanding renewal token don't get included
        '''
        last_update = self._update_time_about_to_go_stale()
        car = self._setup_car_with_update_time(last_update)
        owner_crm.models.Renewal.objects.create(car=car, pk=666)

        command = owner_notifications.Command()
        self.assertFalse(command.notifiable_cars())
