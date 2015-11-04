# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from idlecars import email

from owner_crm.models import notification


class RequestBaseLetter(notification.StreetTeamNotification):
    def get_context(self, **kwargs):
        context = {
            'FNAME': 'Street Team',
            'HEADLINE': 'Base letter request for {}'.format(kwargs['driver_full_name']),
            'TEXT': '''
                We have a new driver that needs a base letter. Please reply with a photo of the letter.
                <br />
                Name: {} <br />
                Email: {} <br />
                Phone number: {} <br />
                TLC plate number: {}
            '''.format(
                kwargs['driver_full_name'],
                kwargs['driver_email'],
                kwargs['driver_phone_number'],
                kwargs['car_plate'],
            ),
            'CTA_LABEL': 'Call (844) 435-3227',
            'CTA_URL': 'tel:1-844-4353227',
            'CAR_IMAGE_URL': kwargs['fhv_license_image'],
            'subject': 'Base letter request for {}'.format(kwargs['driver_full_name']),
            'template_name': 'one_button_one_image',
        }
        return context
