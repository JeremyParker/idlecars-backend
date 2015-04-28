# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from collections import OrderedDict

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
        owner = factories.Owner(state_code='NY')
        owner.save()

        make_model = factories.MakeModel()
        make_model.save()

        self.car = factories.Car(
            owner=owner,
            make_model=make_model,
            status='busy',
            next_available_date=datetime.date.today() + datetime.timedelta(days=1),
            min_lease='_03_two_weeks',
            hybrid=True,
        )
        self.car.save()

    def test_get_cars(self):
        url = reverse('server:cars-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        listing_features = '{} minimum lease ∙ Available {} ∙ {}, {}'
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
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
                    ('image_url', 'https://s3.amazonaws.com/images.idlecars.com/toyota_avalon.jpg')
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
        car = factories.Car()
        car.save()

        user = factories.UserAccount()
        json = '''{{
            "user_account": {{
                "first_name": "{}",
                "last_name": "{}",
                "phone_number": "{}",
                "email": "{}"
            }},
            "car_id": {}
        }}'''.format(
            user.first_name,
            user.last_name,
            user.phone_number,
            user.email,
            car.pk
        )

        stream = BytesIO(json)
        data = JSONParser().parse(stream)
        serializer = BookingSerializer(data=data)
        serializer.is_valid()
        booking = serializer.save()
        self.assertEqual(booking.car.pk, car.pk)
        self.assertEqual(booking.user_account.first_name, user.first_name)
        self.assertEqual(booking.user_account.last_name, user.last_name)
        self.assertEqual(booking.user_account.phone_number, user.phone_number)
        self.assertEqual(booking.user_account.email, user.email)


class BookingTest(APITestCase):
    def setUp(self):
        self.car = factories.Car()
        self.car.save()
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
