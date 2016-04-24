# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.conf import settings

from idlecars import email, fields

from server import models

from owner_crm.models import notification


class DocumentsUploaded(notification.OpsNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': 'operations team',
            'HEADLINE': 'Driver Docs uploaded!',
            'TEXT': 'Someone with the number {} uploaded all thier docs. No action is required'.format(
                kwargs['driver_phone_number']
            ),
            'CTA_LABEL': 'View the Driver record',
            'CTA_URL': kwargs['driver_admin_link'],
            'template_name': 'one_button_no_image',
            'subject': 'Uploaded documents from {}'.format(kwargs['driver_phone_number']),
        }


class InsuranceApproved(notification.OpsNotification):
    def get_context(self, **kwargs):
        headline = '{} has been approved on the {} with medallion {}.'.format(
            kwargs['driver_full_name'] or 'A driver',
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = '''
            {} has approved the request for {} to be added to their medallion: {}.
            All the required documentation is encosed below. If there is no MVR image attached
            then the owner has accepted the charge for us to run an MVR on his behalf'''.format(
                kwargs['owner_name'],
                kwargs['driver_full_name'] or 'A driver',
                kwargs['car_plate'],
            )

        context = {
            'PREVIEW': headline,
            'FNAME': 'operations team',
            'HEADLINE': headline,
            'TEXT0': text,
            'IMAGE_1_URL': kwargs['driver_license_image'],
            'TEXT1': 'DMV License <a href="{}">(click here to download)</a>'.format(
                kwargs['driver_license_image']
            ),
            'IMAGE_2_URL': kwargs['fhv_license_image'],
            'TEXT2': 'Hack License <a href="{}">(click here to download)</a>'.format(
                kwargs['fhv_license_image']
            ),
            'IMAGE_3_URL': kwargs['address_proof_image'],
            'TEXT3': 'MVR <a href="{}">(click here to download)</a>'.format(
                kwargs['address_proof_image']
            ),
            'TEXT5': 'The driver\'s social security number is {}.<br>Questions? Need more documentation? Please call {} at {}.'.format(
                    kwargs['driver_ssn'],
                    kwargs['driver_first_name'] or 'the driver',
                    fields.format_phone_number(kwargs['driver_phone_number']),
                ),
            'CTA_LABEL': 'More details',
            'CTA_URL': kwargs['booking_admin_link'],
            'subject': '{} has approved the request for {} to be added to their medallion: {}'.format(
                kwargs['owner_name'],
                kwargs['driver_full_name'] or 'A driver',
                kwargs['car_plate'],
            ),
            'template_name': 'one_button_three_images',
        }
        return context

class DriverRemoved(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = '''{} has removed {} from their medallion {}.'''.format(
            kwargs['owner_name'],
            kwargs['driver_full_name'] or 'Their driver',
            kwargs['car_plate'],
        )

        return {
            'FNAME': 'operations team',
            'HEADLINE': 'A driver has been removed',
            'TEXT': text,
            'template_name': 'one_button_no_image',
            'subject': 'a driver is being removed from  {}.'.format(kwargs['car_plate']),
            'CTA_LABEL': 'More details',
            'CTA_URL': kwargs['booking_admin_link'],
        }
