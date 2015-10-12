# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import get_template
from django.utils.http import urlquote
from django.conf import settings

from idlecars import email
from idlecars.job_queue import job_queue


def queue_owner_welcome_email(email_address):
    text = '''
    Find more drivers for your idle cars. <br>
    Fill out this form to add your car to our listings. When a qualified driver requests your car, we will contact you directly. <br>
    Questions? Email us at support@idlecars.com, or call ''' + IDLECARS_PHONE_NUMBER
    merge_vars = {
        email_address: {
            'HEADLINE': 'Welcome To Idlecars!',
            'TEXT': text,
            'CTA_LABEL': 'List a car',
            'CTA_URL': 'http://goo.gl/forms/4s26I6GUQY',
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Welcome to idlecars',
        merge_vars=merge_vars,
    )
