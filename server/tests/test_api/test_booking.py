# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token

from server import factories, models, services


class CreateBookingTest(APITestCase):
    def setUp(self):
        self.car = factories.Car.create()
        self.driver = factories.Driver.create()

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-list')
        self.data = {'car': self.car.pk}

    def test_create_booking_success(self):
        """ Ensure we can create a new booking object. """
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['car'], self.car.pk)
        self.assertEqual(response.data['driver'], self.driver.pk)

    def test_create_booking_fail_not_logged_in(self):
        """ Ensure we can't book if not logged in"""
        self.client.credentials()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_booking_fail_when_driver_busy(self):
        """ Ensure we can't book if the driver already has an oustanding booking"""
        other_car = factories.Car.create()
        existing_booking = models.Booking.objects.create(car=other_car, driver=self.driver)
        existing_booking.state = models.Booking.PENDING
        existing_booking.save()
        response = self.client.post(self.url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['_app_notifications'], ['You have a conflicting rental.'])


class ListBookingTest(APITestCase):
    def setUp(self):
        self.driver = factories.Driver.create()
        self.booking = factories.Booking.create(driver=self.driver)

        # populate the db with a bunch of bookings not related to this driver
        for i in range(10):
            factories.Booking.create()

        # Include an appropriate `Authorization:` header on all requests.
        self.client = APIClient()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-list')

    def test_get_booking_list(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        for booking_data in response.data:
            self.assertEqual(booking_data['car']['id'], self.booking.car.pk)

    def test_get_booking_list_one_pending_one_booked(self):
        self.booking.status = models.Booking.BOOKED
        booking2 = factories.Booking.create(driver=self.driver, state=models.Booking.PENDING)

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        ids = [b['car']['id'] for b in response.data]
        self.assertTrue(booking2.car.pk in ids)
        self.assertTrue(self.booking.car.pk in ids)

    def test_canceled_booking_excluded(self):
        self.booking.state = models.Booking.CANCELED
        self.booking.save()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_cancelable_bookings(self):
        for state in models.booking_state.cancelable_states():
            self.booking.state = state
            self.booking.save()
            response = self.client.get(self.url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data[0]['state_details']['cancelable'])

        visible = models.booking_state.visible_states()
        cancelable = models.booking_state.cancelable_states()
        un_cancelable = [s for s in visible if s not in cancelable]

        for state in un_cancelable:
            self.booking.state = state
            self.booking.save()
            response = self.client.get(self.url, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertFalse(response.data[0]['state_details']['cancelable'])


class UpdateBookingTest(APITestCase):
    def setUp(self):
        self.booking = factories.Booking.create(
            state=models.Booking.PENDING,
            end_time=datetime.datetime(2014, 12, 15, 14, tzinfo=timezone.get_current_timezone())
        )

        self.client = APIClient()
        # Include an appropriate `Authorization:` header on all requests.
        token = Token.objects.get(user__username=self.booking.driver.auth_user.username)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))

    def test_cancel_booking_success(self):
        data = { 'state': models.Booking.CANCELED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking = models.Booking.objects.get(id=self.booking.pk)
        self.assertEqual(self.booking.state, models.Booking.CANCELED)

    def test_not_cancel_anothers_booking(self):
        another_booking = factories.Booking.create()
        data = { 'state': models.Booking.CANCELED }
        url = reverse('server:bookings-detail', args=(another_booking.pk,))
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_set_booking_to_non_cancel(self):
        data = { 'state': models.Booking.BOOKED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_booked_booking(self):
        # set the booking to "Booked"
        self.booking.state = models.Booking.BOOKED
        self.booking.save()

        data = { 'state': models.Booking.CANCELED }
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_set_end_time(self):
        data = {'end_time': [2015, 0, 1]}  # happy new year
        response = self.client.patch(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking = models.Booking.objects.get(id=self.booking.pk)
        expected_end = datetime.datetime(2015, 1, 1, tzinfo=timezone.get_current_timezone())
        self.assertEqual(
            self.booking.end_time.astimezone(timezone.get_current_timezone()),
            expected_end
        )


class BookingStepTest(APITestCase):
    '''
    Test that the booking shows the correct steps at the correct times as it
    transitions through all states
    '''
    def test_new_driver_starts(self):
        self.driver = factories.Driver.create()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.booking = factories.Booking.create(driver=self.driver)
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))
        self._pending_no_docs()

    def test_complete_driver_starts(self):
        self.driver = factories.CompletedDriver.create()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.booking = factories.Booking.create(driver=self.driver)
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))
        self._pending_with_docs()

    def test_approved_driver_starts(self):
        self.driver = factories.ApprovedDriver.create()
        token = Token.objects.get(user__username=self.driver.auth_user.username)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.booking = factories.Booking.create(driver=self.driver)
        self.url = reverse('server:bookings-detail', args=(self.booking.pk,))
        self._pending_with_docs()


    def _pending_no_docs(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 2)
        self.assertTrue(response.data['start_time_estimated'])

        # driver uploads their documents
        self.driver.driver_license_image = 'some image'
        self.driver.fhv_license_image = 'some image'
        self.driver.address_proof_image = 'some image'
        self.driver.defensive_cert_image = 'some image'
        self.driver.save()

        self._pending_with_docs()

    def _pending_with_docs(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['step'], 3)
        self.assertTrue(response.data['start_time_estimated'])

        checkout_url = reverse('server:bookings-checkout', args=(self.booking.pk,))
        checkout_response = self.client.post(checkout_url, data={})
        self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)

        self._checked_out_docs_unapproved()

    def _pending_docs_approved(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['step'], 3)
        self.assertTrue(response.data['start_time_estimated'])

        checkout_url = reverse('server:bookings-cancelation')
        checkout_response = self.client.post(checkout_url, args=(self.booking.pk,))
        self.assertEqual(checkout_response.status_code, status.HTTP_200_OK)
        self._checked_out_docs_approved()

    def _checked_out_docs_unapproved(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 4)
        self.assertTrue(response.data['start_time_estimated'])

        # next, the docs get approved...
        self.driver.documentation_approved = True
        self.driver.save()
        self._checked_out_docs_approved()

    def _checked_out_docs_approved(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 4)
        self.assertTrue(response.data['start_time_estimated'])

        # next, the insurance gets accepted
        self.booking.state = models.Booking.ACCEPTED
        self.booking.approval_time = timezone.now()
        self.booking.save()
        self._accepted_booking()

    def _accepted_booking(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 4)
        self.assertFalse(response.data['start_time_estimated'])

        # next the driver picks up the car
        pickup_url = reverse('server:bookings-pickup', args=(self.booking.pk,))
        pickup_response = self.client.post(pickup_url, data={})
        self.assertEqual(pickup_response.status_code, status.HTTP_200_OK)
        self._in_progress_booking()

    def _in_progress_booking(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.data['step'], 5)
        self.assertFalse(response.data['start_time_estimated'])
