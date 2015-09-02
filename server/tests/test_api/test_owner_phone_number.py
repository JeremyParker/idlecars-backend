# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from idlecars import fields

from server import factories, models


class OwnerPhoneNumberTest(APITestCase):
    def setUp(self):
        self.owner = factories.Owner.create()
        self.user_account = factories.UserAccount.create(owner=self.owner)

    # they already signed up, they should just log in
    def test_owner_and_user(self):
        auth_owner = factories.AuthOwner.create()
        phone_number = auth_owner.auth_users.latest('pk').username
        old_account = factories.UserAccount.create(
            owner=auth_owner,
            phone_number=phone_number,
        )
        url = reverse('server:owner_phone_numbers', args=(phone_number,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(phone_number),
        )
        self.assertNotIn('_app_notifications', response.data.keys())

    # they are an owner, but they haven't created a password or auth_user yet
    def test_no_auth_user(self):
        url = reverse('server:owner_phone_numbers', args=(self.user_account.phone_number,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.owner.phone_number())
        )
        self.assertIn('Great, you\'re in our system already!', response.data['_app_notifications'][0])

    # owner who mistakenly signed up as driver too
    def test_driver_and_owner(self):
        driver = factories.Driver.create()
        driver_user_account = factories.UserAccount.create(
            driver=driver,
            owner=self.owner,
            phone_number=driver.auth_user.username,
        )
        url = reverse('server:owner_phone_numbers', args=(driver_user_account.phone_number,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['phone_number'],
            fields.format_phone_number(self.owner.phone_number())
        )
        self.assertIn('Great, you\'re in our system already!', response.data['_app_notifications'][0])

    # not an owner
    def test_no_owner_or_authuser(self):
        driver_user_account = factories.UserAccount.create()
        url = reverse('server:owner_phone_numbers', args=(driver_user_account.phone_number,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Sorry, something went wrong', response.data['_app_notifications'][0])

    # not an owner
    def test_wrong_number(self):
        url = reverse('server:owner_phone_numbers', args=('6663334444',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
