# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models
from server.services import car as car_service
from server.services import tlc_data_service


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

    def test_cannot_update_car(self):
        car = factories.Car.create()
        url = reverse('server:cars-detail', args=(car.pk,))
        response = self.client.patch(url, {'solo_cost': 350}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CarAPITest(APITestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.car = factories.BookableCar.create(
            owner=self.owner,
            plate='REAL_PLATE', # TODO - add this plate to the TLC db
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

    def test_get_incomplete_car_details(self):
        # make an incomplete car (not a BookableCar)
        car = factories.Car.create(
            owner=self.owner,
            plate='OTHER_REAL_PLATE',
            solo_cost=None,
            solo_deposit=None,
        )
        url = reverse('server:cars-detail', args=(car.pk,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], car.pk)
        self.assertEqual(response.data['plate'], car.plate)

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

        # TODO - add a record to the TLC database so we can 'find' it when creating a car.
        factories.Insurance.create()
        self.plate = 'REAL_PLATE'
        self.url = reverse('server:cars-list')

    def test_create_car_success(self):
        self.car = None # forget that we had a car
        plate = 'OTHER_REAL_PLATE'
        response = self.client.post(self.url, data={'plate': plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plate'], plate)
        self.assertEqual(models.Car.objects.get(plate=plate).owner, self.owner)

        # make sure we filled in the stuff we were supposed to fill in
        self.assertIsNotNone(response.data['name'])
        self.assertIsNotNone(response.data['base'])
        self.assertIsNotNone(response.data['insurance'])
        self.assertIsNotNone(response.data['listing_link'])
        self.assertIsNotNone(response.data['status'])
        self.assertIsNotNone(response.data['next_available_date'])

    def test_create_duplicate_i_own(self):
        response = self.client.post(self.url, data={'plate': self.car.plate})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('_app_notifications' in response.data.keys())

    def test_create_other_owners_duplicate(self):
        self.car = None # forget that we had a car
        other_car = factories.Car.create()
        response = self.client.post(self.url, data={'plate': other_car.plate})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('_app_notifications' in response.data.keys())

    def test_unregistered_car_fails(self):
        self.car = None # forget that we had a car
        response = self.client.post(self.url, data={'plate': 'NOT FOUND'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('_app_notifications' in response.data.keys())


class CarUpdateTest(CarAPITest):
    def test_change_car_details(self):
        self.car.solo_cost = None
        self.car.save()

        url = reverse('server:cars-detail', args=(self.car.pk,))
        data = {'solo_cost': 350}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertEqual(self.car.solo_cost, Decimal('350'))

    def test_cannot_update_others_cars(self):
        other_car = factories.Car.create()
        url = reverse('server:cars-detail', args=(other_car.pk,))
        response = self.client.patch(url, {'solo_cost': 350}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_tlc_or_readonly_fields(self):
        read_only_fields = [
            'plate',
            'id',
            'created_time',
            'state',
            'name',
            'listing_link',
        ]
        # get a car through the API to get the available fields and values
        url = reverse('server:cars-detail', args=(self.car.pk,))
        other_car_data = self.client.get(url).data

        new_car = factories.BookableCar.create(owner=self.owner)
        url = reverse('server:cars-detail', args=(new_car.pk,))
        new_car_data = self.client.get(url).data

        for field in other_car_data.keys():
            # print field # - uncomment this to debug this unit test
            original_value = new_car_data.get(field, '1')
            other_value = other_car_data.get(field, '2')

            # try to set the new_car's field to the exising_car's field
            response = self.client.patch(url, {field: other_value}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            current_value = response.data[field]
            if field in tlc_data_service.fhv_fields + read_only_fields:
                # values didn't change for the read-only fields
                self.assertEqual(current_value, original_value)
            else:
                # values changed for the writable fields
                self.assertEqual(current_value, other_value)
