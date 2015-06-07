# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.six import BytesIO

from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase

from server import factories, models
from server.serializers import UserAccountSerializer, BookingSerializer


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


class UserAccountSerializerTest(TestCase):
    def test_deserialize(self):
        json = '''{
            "first_name": "Alexandra",
            "last_name": "Higgins",
            "phone_number": "212-123-4567",
            "email": "someone@somewhere.com"
        }'''
        stream = BytesIO(json)
        data = JSONParser().parse(stream)
        serializer = UserAccountSerializer(data=data)
        serializer.is_valid()
        user_account = serializer.save()
        self.assertEqual(user_account.first_name, "Alexandra")
        self.assertEqual(user_account.last_name, "Higgins")
        self.assertEqual(user_account.phone_number, "212-123-4567")
        self.assertEqual(user_account.email, "someone@somewhere.com")

    def test_deserialize_Fail(self):
        json = '''{
            "first_name": "Alexandra",
            "last_name": "Higgins",
            "phone_number": "212-123-4567",
            "email": ""
        }'''
        stream = BytesIO(json)
        data = JSONParser().parse(stream)
        serializer = UserAccountSerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {'email': [u'This field may not be blank.']})


class BookingSerializerTest(TestCase):
    def test_deserialize(self):
        car = factories.Car.create()
        user = factories.UserAccount.create()
        driver = factories.Driver(user_account=user)

        json = '''{{
            "user_account": {{
                "first_name": "{}",
                "last_name": "{}",
                "phone_number": "{}",
                "email": "{}"
            }},
            "car_id": {}
        }}'''.format(
            driver.user_account.first_name,
            driver.user_account.last_name,
            driver.user_account.phone_number,
            driver.user_account.email,
            car.pk
        )

        stream = BytesIO(json)
        data = JSONParser().parse(stream)
        serializer = BookingSerializer(data=data)
        serializer.is_valid()
        booking = serializer.save()
        self.assertEqual(booking.car.pk, car.pk)
        self.assertEqual(booking.driver.first_name, driver.first_name)
        self.assertEqual(booking.driver.last_name, driver.last_name)
        self.assertEqual(booking.driver.phone_number, driver.phone_number)
        self.assertEqual(booking.driver.email, driver.email)


class BookingTest(APITestCase):
    def setUp(self):
        self.car = factories.Car.create()
        self.data = {
            'user_account': {
                'first_name': 'Alexandra',
                'last_name': 'Higgins',
                'phone_number': '212-234-5678',
                'email': 'someone@somewhere.com',
            },
            'car_id': self.car.pk
        }

    def test_create_booking_success(self):
        """
        Ensure we can create a new booking object.
        """
        url = reverse('server:bookings-list')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['car_id'], self.car.pk)
        self.assertEqual(
            response.data['user_account']['id'],
            models.UserAccount.objects.latest('pk').pk
        )
        self.assertEqual(
            models.Booking.objects.latest('pk').user_account.phone_number,
            self.data['user_account']['phone_number']
        )

    def test_create_booking_fail(self):
        self.data['user_account']['email'] = ''
        url = reverse('server:bookings-list')
        response = self.client.post(url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.content,
            '{"user_account":{"email":["This field may not be blank."]}}'
        )
