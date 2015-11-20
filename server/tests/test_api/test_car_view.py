# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models


class CarAPITest(APITestCase):
    def setUp(self):
        self.owner =  factories.Owner.create()
        self.car = factories.BookableCar.create(
            owner=self.owner,
        )
        self.client = APIClient()
        token = Token.objects.get(user__username=self.owner.auth_users.last().username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


class GetCarListTest(CarAPITest):
    def setUp(self):
        super(GetCarListTest, self).setUp()
        self.url = reverse('server:cars-list')
        self.other_car = factories.Car.create()

    def test_get_car_list(self):
        response = self.client.get(self.url)
        import pdb; pdb.set_trace()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.car.pk)
        self.assertEqual(response.data['plate'], self.car.plate)


class GetCarDetailsTest(CarAPITest):
    def setUp(self):
        super(GetCarListTest, self).setUp()
        self.url = reverse('server:cars-detail', args=(self.car.pk,))

    def test_get_car_details(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.car.pk)
        self.assertEqual(response.data['plate'], self.car.plate)

