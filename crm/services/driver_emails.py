# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes

from server.services import car as car_service
from server.services import driver as driver_service


def documents_approved_no_booking(driver):
    merge_vars = {
        'support@idlecars.com': {
            'FNAME': driver.first_name(),
            'TEXT': 'Your uploaded documents have been reviewed and approved. You are now ready to rent any car on idlecars with one tap!',
            'CTA_LABEL': 'Rent a car now',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='single_cta',
        subject='Welcome to idlecars, {}'.format(booking.driver.full_name()),
        merge_vars=merge_vars,
    )


def _render_reminder_body(booking):
    doc_names = driver_service.get_missing_docs(booking.driver)
    docs = ''
    for name in doc_names[:-1]:
        docs = docs + name + ', '
    docs = docs + 'and ' + doc_names[-1]

    template_data = {
        'CAR_NAME': booking.car.__unicode__(),
        'DOCS_LIST': docs,
    }
    context = Context(autoescape=False)
    return render_to_string("driver_docs_reminder.jade", template_data, context)


def documents_reminder(booking):
    body = _render_reminder_body(booking)
    cta_url = client_side_routes.doc_upload_url()
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name or None,
            'TEXT': body,
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': cta_url,
            'HEADLINE': 'Your {} is waiting'.format(booking.car.__unicode__()),
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='owner_renewal',
        subject='Your {} is waiting on your driving documents'.format(booking.car.__unicode__()),
        merge_vars=merge_vars,
    )
