# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from customer import Customer
from credit_code import CreditCode

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_customer(sender, instance=None, created=False, **kwargs):
    if created:
        Customer.objects.create(user=instance)
