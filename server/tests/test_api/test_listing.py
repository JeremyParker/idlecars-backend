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


class ListingTest(APITestCase):
    def setUp(self):
        self.car = factories.BookableCar.create(
            status='busy',
            next_available_date=timezone.now() + datetime.timedelta(days=1),
            hybrid=False,
            min_lease='_03_two_weeks',
            weekly_rent=100,
        )

    def _get_expected_representation(self, car):
        ''' returns the expected API response for a given car '''
        listing_features = '{} minimum ∙ Available {} ∙ {}, {}'
        booked_features = '{} minimum rental ∙ {}, {}'
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        expected = OrderedDict(
            [
                ('id', car.pk),
                ('name', '{} {}'.format(car.year, car.make_model)),
                ('listing_features', listing_features.format(
                        models.Car.MIN_LEASE_CHOICES[car.min_lease],
                        '{d.month}/{d.day}'.format(d = tomorrow),
                        car.owner.city,
                        car.owner.state_code,
                    )
                ),
                ('headline_features',
                    [
                        'Available {d.month}/{d.day}'.format(d = tomorrow),
                        '{} minimum rental'.format(models.Car.MIN_LEASE_CHOICES[car.min_lease]),
                        '${} deposit'.format(car.deposit),
                    ]
                ),
                ('shift', {'description': '24/7', 'split_shift': False}),
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
                        ['Location', '{}, {}'.format(
                            car.owner.city,
                            car.owner.state_code,
                        )],
                        ['TLC Base', car.base]
                    ]
                ),
                ('deposit', '${}'.format(car.deposit)),
                ('cost_str', ['14', '29']), # this number base on car.weekly_rent, which is $100 in the test
                ('cost_time', 'a day'),
                ('cost_bucket', ['cheap']),
                ('searchable', {'body_type': ['Sedan'], 'lux_level': ['Standard'], 'cost_bucket': ['cheap'], 'work_with': []}),
                ('booked_features', booked_features.format(
                        models.Car.MIN_LEASE_CHOICES[car.min_lease],
                        car.owner.city,
                        car.owner.state_code,
                    )
                ),
                ('image_url', None),
                ('zipcode', car.owner.zipcode),
                ('compatibility', []),
            ]
        )

        if car.interior_color is not None:
            expected['details'] = [['Interior color', models.Car.COLOR_CHOICES[car.interior_color][1]],] + expected['details']
        if car.exterior_color is not None:
            expected['details'] = [['Exterior color', models.Car.COLOR_CHOICES[car.exterior_color][1]],] + expected['details']
        if car.display_mileage():
            expected['details'] = [['Mileage', '{},000'.format(car.last_known_mileage / 1000)],] + expected['details']
        if car.hybrid:
            expected['details'] = [['Hybrid ☑', ''],] + expected['details']
        return dict(expected)

    def test_get_cars(self):
        url = reverse('server:listings-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rep = self._get_expected_representation(self.car)
        self.assertEqual([rep], response.data)

    def test_get_cars_sorted(self):
        for _ in range(20):
            factories.BookableCar.create()
        url = reverse('server:listings-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        previous_car_cost = 0
        for car in response.data:
            self.assertTrue(int(car['cost_str'][0]) >= previous_car_cost)
            previous_car_cost = int(car['cost_str'][0])

    def _assert_car_details(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self._get_expected_representation(self.car))

    def test_get_live_car(self):
        url = reverse('server:listings-detail', args=(self.car.pk,))
        self._assert_car_details(self.client.get(url, format='json'))

    def test_get_unlisted_car(self):
        # make it so the car is unlisted (all info complete, but not live)
        self.car.owner.merchant_account_state = models.Owner.BANK_ACCOUNT_DECLINED
        self.car.owner.save()
        url = reverse('server:listings-detail', args=(self.car.pk,))
        self._assert_car_details(self.client.get(url, format='json'))

    def test_get_unlistable_car(self):
        # make it so this car has incomplete information, so it can't be shown at all
        self.car.plate = ''
        self.car.save()
        url = reverse('server:listings-detail', args=(self.car.pk,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_car_with_all_fields(self):
        self.car = factories.CompleteCar.create(
            next_available_date=timezone.now() + datetime.timedelta(days=1),
            exterior_color=0,
            interior_color=0,
            min_lease='_03_two_weeks',
            weekly_rent=100, # make it ridiculously cheap, so it's always in the 'cheap' bucket
        )
        url = reverse('server:listings-detail', args=(self.car.pk,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = self._get_expected_representation(self.car)
        expected['details'][2] = ['Exterior color', 'Black']
        expected['details'][3] = ['Interior color', 'Black']

        self.assertEqual(response.data, expected)
