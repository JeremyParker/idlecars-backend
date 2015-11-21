# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models


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


class CarDetailsTest(CarAPITest):
    def setUp(self):
        super(CarDetailsTest, self).setUp()
        self.url = reverse('server:cars-detail', args=(self.car.pk,))

    def test_get_car_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.car.pk)
        self.assertEqual(response.data['plate'], self.car.plate)


class CarCreateTest(CarAPITest):
    def setUp(self):
        super(CarCreateTest, self).setUp()
        self.url = reverse('server:cars-list')
        self.plate = 'T208340C'
        # TODO - add a record to the TLC database so we can 'find' it when creating a car.

    def test_create_car_success(self):
        response = self.client.post(self.url, data={'plate': self.plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plate'], self.plate)


    # test owner can update a car they just created
    # test can't update plate

    # TODO
    # test authenticated driver can't create a car
