# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import braintree

from django.conf import settings
from django.test import Client, TestCase
from django.core.urlresolvers import reverse

from owner_crm.tests import sample_merge_vars
from idlecars import client_side_routes
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
        with self.settings(PAYMENT_GATEWAY_NAME='braintree'):
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

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(outbox[0].subject, 'Your bank account has been approved.')
        self.assertEqual(outbox[0].merge_vars.keys()[0], self.owner.auth_users.first().email)
        self.assertEqual(
            outbox[0].merge_vars[self.owner.auth_users.first().email]['CTA_URL'],
            client_side_routes.add_car_form(),
        )
        self.assertTrue(sample_merge_vars.check_template_keys(outbox))

    def test_webhook_declined(self):
        with self.settings(PAYMENT_GATEWAY_NAME='braintree'):
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

        from django.core.mail import outbox
        self.assertEqual(len(outbox), 1)
        merge_vars = outbox[0].merge_vars[settings.OPS_EMAIL]
        self.assertTrue('<ul><li>' in merge_vars['TEXT'])

    def test_webhook_no_owner(self):
        with self.settings(PAYMENT_GATEWAY_NAME='braintree'):
            sample_notification = braintree.WebhookTesting.sample_notification(
                braintree.WebhookNotification.Kind.SubMerchantAccountApproved,
                'some_wrong_id',
            )
            url = reverse('bt_hooks:submerchant_create_success')
            response = self.client.post(url, data=sample_notification)
            self.assertEquals(404, response.status_code)
