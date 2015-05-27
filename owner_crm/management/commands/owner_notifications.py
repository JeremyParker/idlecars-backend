# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, client_side_routes
from server.services import car as car_service
from owner_crm.models import Renewal

class Command(BaseCommand):
    help = 'Sends notifications to owners about the state of their cars'

    def handle(self, *args, **options):
        for car in self.notifiable_cars():
            renewal = Renewal.objects.create(car=car)
            renewal_url = client_side_routes.renewal_url(renewal)
            body = self.render_body(car)

            for user in car.owner.user_account.all():
                merge_vars = {
                    user.email: {
                        'FNAME': user.first_name or None,
                        'TEXT': body,
                        'CTA_LABEL': 'Renew Listing Now',
                        'CTA_URL': renewal_url,
                    }
                }
                email.send_async(
                    template_name='single_cta',
                    subject='Your {} listing is about to expire.'.format(car.__unicode__()),
                    merge_vars=merge_vars,
                )

    def notifiable_cars(self):
        # TODO - optimize this query
        oustanding_renewal_cars = [r.car.id for r in Renewal.objects.filter(state=Renewal.STATE_PENDING)]
        return car_service.get_stale_within(
            minutes_until_stale=60 * 2,
        ).exclude(
            id__in = oustanding_renewal_cars,
        )

    def render_body(self, car):
        template_data = {
            'CAR_NAME': car.__unicode__(),
            'CAR_PLATE': car.plate,
        }
        context = Context(autoescape=False)
        return render_to_string("car_expiring.jade", template_data, context)
