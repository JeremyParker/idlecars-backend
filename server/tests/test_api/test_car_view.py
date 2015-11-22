# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models


class CarUnauthorizedTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_cannot_get_cars(self):
        url = reverse('server:cars-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_get_car_details(self):
        car = factories.Car.create()
        url = reverse('server:cars-detail', args=(car.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_create_car(self):
        url = reverse('server:cars-list')
        response = self.client.post(url, data={'plate': 'FAKE_PLATE'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def authenticated_driver_cannot_create_car(self):
        driver = factories.Driver.create()
        token = Token.objects.get(user__username=driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('server:cars-list')
        response = self.client.post(url, data={'plate': 'FAKE_PLATE'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CarAPITest(APITestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.car = factories.BookableCar.create(
            owner=self.owner,
        )
        self.client = APIClient()
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class CarListTest(CarAPITest):
    def setUp(self):
        super(CarListTest, self).setUp()
        self.url = reverse('server:cars-list')

    def test_get_car_list_only_has_my_cars(self):
        other_car = factories.Car.create()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['plate'], self.car.plate)
        self.assertFalse(other_car.plate in [c['plate'] for c in response.data])


class CarDetailsTest(CarAPITest):
    def setUp(self):
        super(CarDetailsTest, self).setUp()

    def test_get_car_details(self):
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.car.pk)
        self.assertEqual(response.data['plate'], self.car.plate)

    def test_cannot_get_another_owners_car(self):
        other_car = factories.BookableCar.create()
        url = reverse('server:cars-detail', args=(other_car.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_404(self):
        url = reverse('server:cars-detail', args=('99999',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CarCreateTest(CarAPITest):
    def setUp(self):
        super(CarCreateTest, self).setUp()
        self.car = None # forget that we had a car

        # TODO - add a record to the TLC database so we can 'find' it when creating a car.
        factories.Insurance.create()
        self.plate = 'T208340C'
        self.url = reverse('server:cars-list')

    def test_create_car_success(self):
        response = self.client.post(self.url, data={'plate': self.plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plate'], self.plate)

        # make sure we filled in the stuff we were supposed to fill in
        self.assertIsNotNone(response.data['name'])
        self.assertIsNotNone(response.data['base'])
        self.assertIsNotNone(response.data['insurance'])
        self.assertIsNotNone(response.data['listing_link'])
        self.assertIsNotNone(response.data['status'])
        self.assertIsNotNone(response.data['next_available_date'])

    # test owner can update a car they just created
    # test can't update plate
