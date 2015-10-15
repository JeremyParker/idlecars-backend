# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from idlecars import email


def request_base_letter(booking):
    merge_vars = {
        settings.STREET_TEAM_EMAIL: {
            'FNAME': 'Street Team',
            'HEADLINE': 'Base letter request for {}'.format(booking.driver.full_name()),
            'TEXT': '''
                We have a new driver that needs a base letter. Please reply with a photo of the letter.
                <br />
                Name: {} <br />
                Email: {} <br />
                Phone number: {} <br />
                TLC plate number: {}
            '''.format(
                booking.driver.full_name,
                booking.driver.email(),
                booking.driver.phone_number(),
                booking.car.plate
            ),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'CAR_IMAGE_URL': booking.driver.fhv_license_image,
        }
    }
    email.send_sync(
        template_name='one_button_one_image',
        subject='Base letter request for {}'.format(booking.driver.full_name()),
        merge_vars=merge_vars,
    )
