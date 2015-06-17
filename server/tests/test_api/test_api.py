# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from server import factories, models
from server.serializers import UserAccountSerializer


class CarTest(APITestCase):
    def setUp(self):
        owner = factories.Owner.create(state_code='NY')
        make_model = factories.MakeModel.create()
        self.car = factories.Car.create(
            owner=owner,
            make_model=make_model,
            status='busy',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )

    def test_get_cars(self):
        url = reverse('server:cars-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listing_features = '{} minimum lease ∙ Available {} ∙ {}, {}'
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        expected = [
            OrderedDict(
                [
                    ('id', self.car.pk),
                    ('name', '{} {}'.format(self.car.year, self.car.make_model)),
                    ('listing_features', listing_features.format(
                            models.Car.MIN_LEASE_CHOICES[self.car.min_lease],
                            '{d.month}/{d.day}'.format(d = tomorrow),
                            self.car.owner.city,
                            self.car.owner.state_code,
                        )),
                    ('headline_features',
                        [
                            'Available {d.month}/{d.day}'.format(d = tomorrow),
                            '{} minimum'.format(models.Car.MIN_LEASE_CHOICES[self.car.min_lease]),
                            '${} deposit'.format(self.car.solo_deposit),
                        ]
                    ),
                    ('certifications',
                        [
                            'Base registration verified',
                            'Vehicle has TLC plates',
                            'Insurance is included',
                            'Maintainance is included',
                        ]
                    ),
                    ('details',
                        [
                            ['Hybrid ☑', ''],
                            ['Location', '{}, {}'.format(
                                self.car.owner.city,
                                self.car.owner.state_code,
                            )],
                            ['TLC Base', self.car.base]
                        ]
                    ),
                    ('cost', '{0:.0f}'.format(self.car.solo_cost)),
                    ('cost_time', 'a week'),
                    ('image_url', None),
                    ('zipcode', self.car.owner.zipcode),
                ]
            )
        ]
        self.assertEqual(response.data, expected)
