# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes

from server.services import car as car_service


def documents_approved_no_booking(driver):
    if not driver.email():
        return
    merge_vars = {
        driver.email(): {
            'FNAME': driver.first_name(),
            'HEADLINE': 'Your documents have been reviewed and approved.',
            'TEXT': 'You are now ready to rent any car on idlecars with one tap!',
            'CTA_LABEL': 'Rent a car now',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Welcome to idlecars, {}!'.format(driver.full_name()),
        merge_vars=merge_vars,
    )


def _missing_documents_text(driver):
    from server.services import driver as driver_service
    doc_names = driver_service.get_missing_docs(driver)
    docs = ''
    for name in doc_names[:-1]:
        docs = docs + '<li>' + name + ', '
    if docs:
        docs = docs + 'and'
    docs = docs + '<li>' + doc_names[-1]
    return docs


def _render_reminder_body(booking):
    docs = _missing_documents_text(booking.driver)
    template_data = {
        'CAR_NAME': booking.car.__unicode__(),
        'DOCS_LIST': docs,
    }
    context = Context(autoescape=False)
    return render_to_string("driver_docs_reminder.jade", template_data, context)


def documents_reminder(booking):
    if not booking.driver.email() or booking.driver.all_docs_uploaded():
        return

    body = _render_reminder_body(booking)
    cta_url = client_side_routes.doc_upload_url()
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': body,
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': cta_url,
            'HEADLINE': 'Your {} is waiting'.format(booking.car.__unicode__()),
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject='Your {} is waiting on your driving documents'.format(booking.car.__unicode__()),
        merge_vars=merge_vars,
    )


def documents_approved(booking):
    if not booking.driver.email():
        return
    template_data = {
        'CAR_NAME': booking.car.__unicode__(),
    }
    context = Context(autoescape=False)
    body = render_to_string("driver_docs_approved.jade", template_data, context)

    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': body,
            'CTA_LABEL': 'See your car',  # TODO: send them to their booking details
            'CTA_URL': client_side_routes.car_details_url(booking.car),
            'HEADLINE': 'Your documents have been reviewed and approved',
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject='Your documents have been reviewed and approved',
        merge_vars=merge_vars,
    )


def someone_else_booked(booking):
    if not booking.driver.email():
        return
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'Someone else rented your car!',
            'TEXT': '''While we were waiting for you to finish uploading your documents,
                another driver rented your car. But don't worry,
                there are plenty more cars available.'''.format(booking.car.__unicode__()),
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Someone else rented your {}.'.format(booking.car.__unicode__()),
        merge_vars=merge_vars,
    )


def booking_canceled(booking):
    if not booking.driver.email():
        return
    body = '''
    Your {} rental has been canceled. Now you can go back to idlecars and rent another car!
    '''
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': body.format(booking.car.__unicode__()),
            'CTA_LABEL': 'Find another car',
            'CTA_URL': client_side_routes.car_listing_url(),
            'HEADLINE': 'Your rental has been canceled',
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject='Confirmation: Your rental has been canceled.',
        merge_vars=merge_vars,
    )


def password_reset(password_reset):
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'HEADLINE': 'Reset your password',
            'TEXT': '''
            We've received a request to reset your password.
            If you didn't make the request, just ignore this email.
            Otherwise, you can reset your password using this link:''',
            'CTA_LABEL': 'Reset password',
            'CTA_URL': client_side_routes.password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Reset your password on idlecars.',
        merge_vars=merge_vars,
    )


def password_reset_confirmation(password_reset):
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'HEADLINE': 'Your password has been reset',
            'TEXT': '''
            Your password has been set. Welcome back! If you didn't
            reset your password, or if you think something funny is going
            on, please call us any time at 1-844-IDLECAR (1-844-435-3227).
            ''',
            'CTA_LABEL': 'Find your car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Your idlecars password has been reset.',
        merge_vars=merge_vars,
    )


# email for the one-time mailer we send out to legacy users
def account_created(password_reset):
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'HEADLINE': 'An account has been created for you at idlecars.',
            'TEXT': '''
            All your documents have been approved and added to your profile. To claim your idlecars
            account all you need to do is tap the button below. Add a password in the form
            and your account will be secured. Then you can rent any car you need, any time you need it.
            ''',
            'CTA_LABEL': 'Claim your account',
            'CTA_URL': client_side_routes.password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Reset your password on idlecars.',
        merge_vars=merge_vars,
    )
