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


class CarTest(APITestCase):
    def setUp(self):
        self.car = factories.BookableCar.create(
            status='busy',
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            hybrid=False,
            min_lease='_03_two_weeks',
        )

    def _get_expected_representation(self, car):
        ''' returns the expected API response for a given car '''
        listing_features = '{} minimum rental ∙ Available {} ∙ {}, {}'
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        expected = OrderedDict(
            [
                ('id', car.pk),
                ('name', '{} {}'.format(car.year, car.make_model)),
                ('listing_features', listing_features.format(
                        models.Car.MIN_LEASE_CHOICES[car.min_lease],
                        '{d.month}/{d.day}'.format(d = tomorrow),
                        car.owner.city,
                        car.owner.state_code,
                    )),
                ('headline_features',
                    [
                        'Available {d.month}/{d.day}'.format(d = tomorrow),
                        '{} minimum'.format(models.Car.MIN_LEASE_CHOICES[car.min_lease]),
                        '${} deposit'.format(car.solo_deposit),
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
                        ['Location', '{}, {}'.format(
                            car.owner.city,
                            car.owner.state_code,
                        )],
                        ['TLC Base', car.base]
                    ]
                ),
                ('cost', '{0:.0f}'.format(car.solo_cost)),
                ('cost_time', 'a week'),
                ('image_url', None),
                ('zipcode', car.owner.zipcode),
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
        url = reverse('server:cars-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rep = self._get_expected_representation(self.car)
        self.assertEqual([rep], response.data)

    def test_get_car(self):
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self._get_expected_representation(self.car))

    def test_get_car_with_all_fields(self):
        self.car = factories.CompleteCar.create(
            next_available_date=timezone.now().date() + datetime.timedelta(days=1),
            exterior_color=0,
            interior_color=0,
            min_lease='_03_two_weeks',
        )
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected = self._get_expected_representation(self.car)
        expected['details'][2] = ['Exterior color', 'Black']
        expected['details'][3] = ['Interior color', 'Black']

        self.assertEqual(response.data, expected)
