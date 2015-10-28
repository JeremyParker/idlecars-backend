# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

import server.factories
from server.models import Car
import server.services.car
import owner_crm.factories
from owner_crm import models


class RenewalUpdateTest(APITestCase):
    def setUp(self):
        car = server.factories.CarExpiredListing.create()
        self.renewal = owner_crm.factories.Renewal.create(car=car)

    def test_update_state(self):
        self.assertEqual(self.renewal.state, models.Renewal.STATE_PENDING)
        self.assertEqual(self._listed_cars_count(), 0)

        url = reverse('owner_crm:renewals-detail', args=(self.renewal.token,))
        response = APIClient().patch(url, {'state': models.ConsumableToken.STATE_CONSUMED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self._assert_renewed()
        self.assertEqual(self._listed_cars_count(), 1)

    def _assert_renewed(self):
        renewal = models.Renewal.objects.get(id=self.renewal.id)
        self.assertEqual(renewal.state, models.ConsumableToken.STATE_CONSUMED)

    def _listed_cars_count(self):
        return server.services.car.filter_live(Car.objects.all()).count()
