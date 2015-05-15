# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.utils.six import BytesIO

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from owner_crm import factories, models


class RenewalUpdateTest(APITestCase):
    def setUp(self):
        self.renewal = factories.Renewal.create()

    def test_update_state(self):
        self.assertEqual(self.renewal.state, models.Renewal.STATE_PENDING)

        url = reverse('owner_crm:renewals-detail', args=(self.renewal.token,))
        response = APIClient().patch(url, {'state': models.Renewal.STATE_RENEWED})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        renewal = models.Renewal.objects.get(id=self.renewal.id)
        self.assertEqual(renewal.state, models.Renewal.STATE_RENEWED)
