# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import decimal

from braintree.test.nonces import Nonces

from django.core.urlresolvers import reverse
from django.contrib import auth

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from credit.models import CreditCode
from credit import credit_service
from idlecars import fields
from idlecars.factories import AuthUser
from server import factories, models


class AuthenticatedDriverTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:drivers-detail', args=(self.driver.id,))


class DriverRetrieveTest(AuthenticatedDriverTest):
    def _test_successful_get(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for k, v in response.data.iteritems():
            driver_val = getattr(self.driver, k, None)
            if callable(driver_val):
                driver_val = driver_val()
            if k == 'phone_number':
                driver_val = fields.format_phone_number(driver_val)
            elif k == 'app_credit':
                driver_val = '${}'.format(driver_val)
            elif k in ['payment_method', 'invite_code',]: # these are different serializers
                continue
            self.assertEqual(response.data[k], driver_val)

    def test_get_driver_as_me(self):
        response = self.client.get(self.url, {'pk': 'me'})
        self._test_successful_get(response)

    def test_get_driver_by_id(self):
        response = self.client.get(self.url, {'pk': self.driver.pk})
        self._test_successful_get(response)

    def test_get_driver_fails_unauthorized(self):
        self.client.credentials()
        response = self.client.get(self.url, {'pk': 'me'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_we_show_default_payment_method(self):
        factories.PaymentMethod.create(driver=self.driver)
        factories.PaymentMethod.create(driver=self.driver, suffix='1234')
        response = self.client.get(self.url, {'pk': self.driver.pk})
        self.assertEqual(response.data['payment_method']['suffix'], '1234')

    def test_sms_method(self):
        get_response = self.client.get(self.url, {'pk': self.driver.pk})
        self.assertTrue(get_response.data['sms_enabled'])
        patch_response = self.client.patch(self.url, {'sms_enabled': False})
        self.assertFalse(patch_response.data['sms_enabled'])

    def test_app_credit(self):
        self.driver.auth_user.customer.app_credit = decimal.Decimal('55.00')
        self.driver.auth_user.customer.save()
        response = self.client.get(self.url, {'pk': self.driver.pk})
        self._test_successful_get(response)
        self.assertEqual(response.data['app_credit'], '$55.00')

    def test_invite_code(self):
        code = credit_service.create_invite_code('10.00', '20.00', self.driver.auth_user.customer)
        response = self.client.get(self.url, {'pk': self.driver.pk})
        self._test_successful_get(response)
        self.assertEqual(response.data['invite_code']['credit_code'], code.credit_code)
        self.assertEqual(
            response.data['invite_code']['credit_amount'],
            '${}'.format(code.credit_amount),
        )
        self.assertEqual(
            response.data['invite_code']['invitor_credit_amount'],
            '${}'.format(code.invitor_credit_amount),
        )


class DriverUpdateTest(AuthenticatedDriverTest):
    def test_update_incomplete_model(self):
        # set up a driver with nothing more than phone number and password
        auth_user = auth.models.User.objects.create(username='1112223333')
        auth_user.set_password('test_pass')
        driver = models.Driver.objects.create(auth_user=auth_user)

        self.client = APIClient()
        token = Token.objects.get(user__username=driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:users-detail', args=(auth_user.id,))

        response = self.client.patch(self.url, {'email': 'test@testing.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_user.refresh_from_db()
        self.assertEqual(driver.email(), 'test@testing.com')

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Welcome to Idlecars')

    def test_update_username_with_full_me(self):
        data = {
            'address_proof_image': "",
            'all_docs_uploaded': False,
            'client_display': "1112220987",
            'defensive_cert_image': "",
            'driver_license_image': "",
            'fhv_license_image': "",
            'id': 201,
        }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_password_forbidden(self):
        response = self.client.patch(self.url, {'password': 'new_password'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check that the old password still works
        self.client.credentials()
        result = self.client.login(username=self.driver.phone_number(), password='password')
        self.assertTrue(result)

    def test_update_image_field(self):
        self.assertEqual(self.driver.driver_license_image, '')
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._driver_reloaded().driver_license_image, 'newurl')

    # def test_redeem_bad_referral_code(self):
    #     response = self.client.patch(self.url, {'invitor_code': 'BADCODE'})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(response.data['_app_notifications'], ['Sorry, we don\'t recognize this code.'])

    # def test_redeem_not_new_driver(self):
    #     factories.BookedBooking.create(driver=self.driver)
    #     code = credit_service.create_invite_code('20.00')
    #     response = self.client.patch(self.url, {'invitor_code': code.credit_code})
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertEqual(
    #         response.data['_app_notifications'],
    #         ['Sorry, referral codes are for new drivers only.']
    #     )

    # def test_redeem_success(self):
    #     code = credit_service.create_invite_code('20.00')
    #     response = self.client.patch(self.url, {'invitor_code': code.credit_code})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data['app_credit'], '$20.00')

    def test_fails_when_not_owner(self):
        other_driver = factories.Driver.create()
        url = reverse('server:drivers-detail', args=(other_driver.id,))
        response = self.client.patch(url, {'driver_license_image': 'newurl'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_fails_when_logged_out(self):
        self.client.credentials()
        response = self.client.patch(self.url, {'driver_license_image': 'newurl'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _driver_reloaded(self):
        return models.Driver.objects.get(id=self.driver.id)


class DriverCreateTest(APITestCase):
    def setUp(self):
        self.url = reverse('server:drivers-list')

    def test_create_driver(self):
        data = {'phone_number': '212 413 1234', 'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['phone_number'], '(212) 413-1234')
        self.assertFalse('password' in response.data)

        stored_phone_number = ''.join([n for n in response.data['phone_number'] if n.isdigit()])

        # check that it was created in the db
        new_driver = models.Driver.objects.get(auth_user__username=stored_phone_number)
        self.assertIsNotNone(new_driver)

        #check that the password works
        self.client.logout()
        self.assertTrue(self.client.login(username=stored_phone_number, password='test'))

    def test_create_driver_fails_with_existing_auth_user(self):
        self.auth_user = AuthUser.create()

        self.client = APIClient()
        data = {'phone_number': self.auth_user.username, 'password': 'new_password'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_password(self):
        data = {'phone_number': '212-413-1234'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_driver_fails_with_no_phone(self):
        data = {'password': 'test'}
        response = APIClient().post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_me_creates_new_driver(self):
        user = AuthUser.create()
        client = APIClient()

        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=user.username)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('server:drivers-detail', args=('me',))
        response = client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        new_driver = models.Driver.objects.get(auth_user=user)
        self.assertEqual(new_driver.phone_number(), user.username)
        self.assertEqual(new_driver.email(), user.email)
        self.assertEqual(new_driver.first_name(), user.first_name)
        self.assertEqual(new_driver.last_name(), user.last_name)


class AddPaymentMethodTest(AuthenticatedDriverTest):
    def setUp(self):
        super(AddPaymentMethodTest, self).setUp()
        self.url = reverse('server:drivers-payment-method', args=(self.driver.pk,))

    def test_add_payment_method(self):
        # TDOO - make a fake_payment gateway response & set it to be returned
        response = self.client.post(self.url, data={'nonce': Nonces.Transactable})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['id'], self.driver.pk)
        self.assertIsNotNone(response.data['payment_method'])
