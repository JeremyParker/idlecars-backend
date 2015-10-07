# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

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

from server.services import owner_service

from freezegun import freeze_time


class TestOwnerNotifications(TestCase):
    def _setup_car_with_update_time(self, update_time):
        car = server.factories.BookableCar.create(
            last_status_update=update_time,
        )
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
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

        subjects = [m.subject for m in outbox]
        for car in cars:
            self.assertTrue('Your {} listing is about to expire.'.format(car.display_name()) in subjects)

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
            self.assertTrue(car.display_name() in var['TEXT'])

    def test_renewable_cars(self):
        '''
        Make sure cars that have an outstanding renewal token don't get included
        '''
        last_update = self._update_time_about_to_go_stale()
        car = self._setup_car_with_update_time(last_update)
        owner_crm.models.Renewal.objects.create(car=car, pk=666)

        self.assertFalse(owner_service._renewable_cars())

    def _new_requested_booking(self, create_time):
        with freeze_time(create_time):
            self.booking = server.factories.RequestedBooking.create()

    @freeze_time("2015-10-11 10:00:00")
    def test_owner_reminder(self):
        self._new_requested_booking("2015-10-10 18:00:00")

        call_command('driver_notifications')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0) # should be 1. not yet set up
        # self.assertTrue(sample_merge_vars.check_template_keys(outbox))
        # self.assertEqual(
        #     outbox[0].subject,
        #     '')
        # )

    def test_reminder_emails_morning_until_failure(self):
        self._new_requested_booking("2015-10-10 18:00:00")

        with freeze_time("2015-10-11 10:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-11 17:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-12 10:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-12 17:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-13 10:00:00"):
            call_command('owner_notifications')

        #TODO: we will have owner reminder email once the text ready
        '''
            - message to owner: first morning reminder
            - message to owner: first afternoon reminder
            - message to owner: second morning reminder
            - message to owner: second afternoon reminder
            - message to owner: insurance too slow reminder
            - message to driver: insurance failed reminder
        '''
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0) #should be 6

    def test_reminder_emails_afternoon_until_failure(self):
        self._new_requested_booking("2015-10-10 23:00:00")

        with freeze_time("2015-10-11 17:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-12 10:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-12 17:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-13 10:00:00"):
            call_command('owner_notifications')
        with freeze_time("2015-10-13 17:00:00"):
            call_command('owner_notifications')

        #TODO: we will have owner reminder email once the text ready
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 0) #should be 6
