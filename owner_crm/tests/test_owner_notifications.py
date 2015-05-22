# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
import mock

from django.utils import timezone
from django.test import TestCase
from django.core.management import call_command

import server.models
import server.factories
import owner_crm.factories


class TestOwnerNotifications(TestCase):
    def _setup_car_with_update_time(self, update_time):
        owner = server.factories.Owner.create()
        car = server.factories.BookableCar.create(
            last_status_update=update_time,
            owner=owner,
        )
        server.factories.UserAccount.create(owner=owner)
        return car

    def test_whole_enchilada(self):
        now = timezone.now()
        # TODO - get the stale_threshold from config
        last_update = now - datetime.timedelta(days=2, hours=23, minutes=50)

        cars = []
        for i in xrange(2):  # two cars about to go stale
            cars.append(self._setup_car_with_update_time(last_update))

        # one car just renewed to make sure filtering is working
        self._setup_car_with_update_time(now)
 
        call_command('owner_notifications')

        # check what got sent
        from django.core.mail import outbox
        self.assertEqual(len(outbox), 2)

        subjects = [m.subject for m in outbox]
        for car in cars:
            self.assertTrue('Your idlecars listing is about to expire.' in subjects)

        # outbox[0].merge_vars
        # {u'LSteuber@domain.com': {u'CTA_LABEL': u'Renew Listing Now',
        #                           u'CTA_URL': u'localhost:3000/#/cars/4/renewals/SkZDrqMQ8QskcpWzchEY',
        #                           u'FNAME': u'Lakisha',
        #                           u'TEXT': u'<p>You have a listing on idlecars that will expire soon. But don\u2019t worry - you can always renew your listing for free with one tap!</p>\n<p>Hit the link below to renew your 2009 Thompson Gleichner with license plate ID3298OT.</p>\n<p>Thanks for keeping us in the loop!<br>- Your idlecars team\n</p>'}}
