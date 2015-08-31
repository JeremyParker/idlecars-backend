# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree

from django.conf import settings
from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from server import factories
from server.models import Owner


# TODO - improve this testing framework so we don't have a duplicate of this method
def _configure_braintree():
    config = settings.BRAINTREE
    if isinstance(config["environment"], unicode):
        config["environment"] = getattr(braintree.Environment, config["environment"])
    braintree.Configuration.configure(**config)


class WebhookTest(TestCase):
    def setUp(self):
        self.client = Client()  # Reinitialize the client to turn off CSRF
        _configure_braintree()
        self.owner = factories.AuthOwner.create(
            merchant_id='test_id',
            merchant_account_state=Owner.BANK_ACCOUNT_PENDING,
        )


    def test_webhook_success(self):
        sample_notification = braintree.WebhookTesting.sample_notification(
            braintree.WebhookNotification.Kind.SubMerchantAccountApproved,
            self.owner.merchant_id,
        )
        url = reverse('bt_hooks:submerchant_create_success')
        response = self.client.post(url, data=sample_notification)
        self.assertEquals(200, response.status_code)
        self.owner.refresh_from_db()
        self.assertEquals(
            self.owner.merchant_account_state,
            Owner.BANK_ACCOUNT_APPROVED,
        )


    def test_webhook_declined(self):
        sample_notification = braintree.WebhookTesting.sample_notification(
            braintree.WebhookNotification.Kind.SubMerchantAccountDeclined,
            self.owner.merchant_id,
        )
        url = reverse('bt_hooks:submerchant_create_failure')
        response = self.client.post(url, data=sample_notification)
        self.assertEquals(200, response.status_code)
        self.owner.refresh_from_db()
        self.assertEquals(
            self.owner.merchant_account_state,
            Owner.BANK_ACCOUNT_DECLINED,
        )


    def test_webhook_no_owner(self):
        sample_notification = braintree.WebhookTesting.sample_notification(
            braintree.WebhookNotification.Kind.SubMerchantAccountApproved,
            'some_wrong_id',
        )
        url = reverse('bt_hooks:submerchant_create_success')
        response = self.client.post(url, data=sample_notification)
        self.assertEquals(404, response.status_code)
