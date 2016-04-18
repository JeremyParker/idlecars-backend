# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal
import datetime

from django.utils import timezone
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
        response = self.client.patch(url, {'weekly_rent': 350}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CarAPITest(APITestCase):
    ''' this is a base class for the rest of the Test classes in this file '''
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

    def test_list_omits_blank_plate_cars(self):
        self.car.plate = ''
        self.car.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


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
            weekly_rent=None,
            deposit=None,
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
        self.plate = 'REAL_PLATE'
        self.url = reverse('server:cars-list')


    def test_create_unclaimed_car_success(self):
        self.car.owner = None
        self.car.save()
        response = self.client.post(self.url, data={'plate': self.car.plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['plate'], self.car.plate)
        new_car = models.Car.objects.get(pk=response.data['id'])
        self.assertEqual(new_car.owner, self.owner)

    def test_create_duplicate_i_own(self):
        response = self.client.post(self.url, data={'plate': self.car.plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('_app_notifications' not in response.data.keys())

    def test_create_other_owners_duplicate(self):
        self.car = None # forget that we had a car
        other_car = factories.BookableCar.create()
        response = self.client.post(self.url, data={'plate': other_car.plate})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('_app_notifications' not in response.data.keys())

    def test_unregistered_car_fails(self):
        self.car = None # forget that we had a car
        response = self.client.post(self.url, data={'plate': 'ERROR: TLC'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('_app_notifications' in response.data.keys())


class CarUpdateTest(CarAPITest):
    def test_change_car_details(self):
        self.car.weekly_rent = None
        self.car.save()

        url = reverse('server:cars-detail', args=(self.car.pk,))
        data = {'shift_details': 'This car is only available Mondays.'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertEqual(self.car.shift_details, 'This car is only available Mondays.')

    def test_can_unclaim_car(self):
        url = reverse('server:cars-detail', args=(self.car.pk,))
        data = {'owner': None}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertIsNone(self.car.owner)

    def test_can_update_unclaimed_car(self):
        unclaimed_car = factories.Car.create()
        url = reverse('server:cars-detail', args=(unclaimed_car.pk,))
        response = self.client.patch(url, {'owner': self.owner.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_set_busy(self):
        data = {'next_available_date': None}
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertIsNone(self.car.next_available_date)

    def test_set_next_available(self):
        data = {'next_available_date': [2017, 0, 1]}
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        expected_date = datetime.datetime(2017, 1, 1, tzinfo=timezone.get_current_timezone())
        self.assertEqual(self.car.next_available_date, expected_date)

    def test_delete_car_by_deleting_owner(self):
        data = {'owner': None}
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.car.refresh_from_db()
        self.assertIsNone(self.car.owner)

    def test_cannot_delete_car_with_booking_in_progress(self):
        factories.RequestedBooking.create(car=self.car)
        data = {'owner': None}
        url = reverse('server:cars-detail', args=(self.car.pk,))
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['_app_notifications'],
            ['A driver is associated with this shift. Remove the driver, then delete.'],
        )

    def test_cannot_update_others_cars(self):
        other_car = factories.BookableCar.create()
        url = reverse('server:cars-detail', args=(other_car.pk,))
        response = self.client.patch(url, {'weekly_rent': 350}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_update_tlc_or_readonly_fields(self):
        read_only_fields = [
            'plate',
            'id',
            'name',
            'created_time',
            'state',
            'listing_link',
            'available_date_display',
            'min_lease_display',
        ]
        # get a car through the API to get the available fields and values
        url = reverse('server:cars-detail', args=(self.car.pk,))
        other_car_data = self.client.get(url).data

        new_car = factories.BookableCar.create(owner=self.owner)
        url = reverse('server:cars-detail', args=(new_car.pk,))
        new_car_data = self.client.get(url).data

        for field in other_car_data.keys():
            new_car.last_status_update = timezone.now() - datetime.timedelta(days=2) # not now

            # print field # - uncomment this to debug this unit test
            original_value = new_car_data.get(field, '1')
            other_value = other_car_data.get(field, '2')

            # try to set the new_car's field to the exising_car's field
            response = self.client.patch(url, {field: other_value}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            current_value = response.data[field]
            if field in tlc_data_service.tlc_fields + read_only_fields:
                # values didn't change for the read-only fields
                self.assertEqual(current_value, original_value)
            else:
                # values changed for the writable fields
                self.assertEqual(current_value, other_value)
                # last_status_update should have updated too
                new_car.refresh_from_db()
                self.assertEqual(new_car.last_status_update.date(), timezone.now().date())


class CarListingExtensionTest(CarAPITest):
    def test_extend_listing(self):
        self.car.last_status_update = timezone.now() - datetime.timedelta(days=5)
        self.car.save()
        url = reverse('server:cars-extension', args=(self.car.pk,))
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.car.refresh_from_db()
        self.assertEqual(self.car.last_status_update.date(), timezone.now().date())
