# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes
from server.services import car as car_service


def _render_renewal_body(car):
    template_data = {
        'CAR_NAME': car.__unicode__(),
        'CAR_PLATE': car.plate,
    }
    context = Context(autoescape=False)
    return render_to_string("car_expiring.jade", template_data, context)


def renewal_email(car, renewal):
    renewal_url = client_side_routes.renewal_url(renewal)
    body = _render_renewal_body(car)
    car_desc = car.__unicode__()

    for user in car.owner.user_account.all():
        merge_vars = {
            user.email: {
                'FNAME': user.first_name or None,
                'TEXT': body,
                'CTA_LABEL': 'Renew Listing Now',
                'CTA_URL': renewal_url,
                'HEADLINE': 'Your {} listing is about to expire'.format(car_desc),
                'CAR_IMAGE_URL': car_service.get_image_url(car),
            }
        }
        email.send_async(
            template_name='owner_renewal',
            subject='Your {} listing is about to expire.'.format(car_desc),
            merge_vars=merge_vars,
        )


def new_booking_email(car, renewal):
    pass
