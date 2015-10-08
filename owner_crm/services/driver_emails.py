# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes

from server.services import car as car_service


def base_letter_approved_no_booking(driver):
    #TODO: text in this email needs to be updated
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


def base_letter_approved_no_checkout(booking):
    if not booking.driver.email():
        return

    body = render_to_string("base_letter_approved_no_checkout.jade", {}, Context(autoescape=False))

    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': body,
            'CTA_LABEL': 'Reserve now',
            'CTA_URL': client_side_routes.bookings(),
            'HEADLINE': 'Your {} is waiting'.format(booking.car.display_name()),
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Your {} is waiting on your payment information!'.format(booking.car.display_name()),
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


def _render_booking_reminder_body(booking, body_template):
    docs = _missing_documents_text(booking.driver)
    template_data = {
        'CAR_NAME': booking.car.display_name(),
        'DOCS_LIST': docs,
    }
    return render_to_string(body_template, template_data, Context(autoescape=False))


def _docs_reminder_for_booking(booking, subject, body_template):
    cta_url = client_side_routes.doc_upload_url()
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': _render_booking_reminder_body(booking, body_template),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': cta_url,
            'HEADLINE': 'Your {} is waiting'.format(booking.car.display_name()),
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject=subject,
        merge_vars=merge_vars,
    )


def _render_driver_reminder_body(driver, body_template):
    docs = _missing_documents_text(driver)
    template_data = {
        'DOCS_LIST': docs,
    }
    return render_to_string(body_template, template_data, Context(autoescape=False))


def _docs_reminder_for_driver(driver, subject, body_template):
    merge_vars = {
        driver.email(): {
            'FNAME': driver.first_name() or None,
            'TEXT': _render_driver_reminder_body(driver, body_template),
            'CTA_LABEL': 'Upload Documents Now',
            'CTA_URL': client_side_routes.doc_upload_url(),
            'HEADLINE': 'Don\'t forget to upload your documents for idlecars',
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject=subject,
        merge_vars=merge_vars,
    )


def documents_reminder(driver, subject, body_template):
    if not driver.email() or driver.all_docs_uploaded():
        return

    pending_bookings = driver.booking_set.all()

    if pending_bookings:
        booking = pending_bookings.order_by('created_time').last()
        subject[0] = subject[0].format(booking.car.display_name())
        _docs_reminder_for_booking(booking, subject[0], body_template[0])
    else:
        _docs_reminder_for_driver(driver, subject[1], body_template[1])


def first_documents_reminder(driver):
    subject = [
        'Your {} is waiting on your driver documents',
        'Submit your documents now so you are ready to drive later.'
    ]
    body_template = [
        'first_docs_reminder_booking.jade',
        'first_docs_reminder_driver.jade'
    ]

    documents_reminder(driver, subject, body_template)


def second_documents_reminder(driver):
    subject = [
        'Your {} is still waiting on your driver documents',
        'Are you ready to drive?'
    ]
    body_template = [
        'second_docs_reminder_booking.jade',
        'second_docs_reminder_driver.jade'
    ]

    documents_reminder(driver, subject, body_template)


def third_documents_reminder(driver):
    subject = [
        'Don’t miss your booking, submit your driver documents',
        'Submit your documents now so you are ready to drive later.'
    ]
    body_template = [
        'third_docs_reminder_booking.jade',
        'third_docs_reminder_driver.jade'
    ]

    documents_reminder(driver, subject, body_template)


def flake_reminder(driver):
    subject = [
        'Your booking has been cancelled because we don\'t have your driver documents',
        'Submit your documents now so you are ready to drive later.'
    ]
    body_template = [
        'flake_reminder_booking.jade',
        'flake_reminder_driver.jade'
    ]

    documents_reminder(driver, subject, body_template)


def awaiting_insurance_email(booking):
    if not booking.driver.email():
        return
    template_data = {
        'CAR_NAME': booking.car.display_name(),
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
        subject='Congratulations! Your documents have been submitted!',
        merge_vars=merge_vars,
    )


def request_base_letter(driver):
    if not driver.email():
        return
    #TODO: send street team email to get base letter


def base_letter_rejected(driver):
    if not driver.email():
        return
    #TODO: send something to driver


def insurance_approved(booking):
    if not booking.driver.email():
        return

    template_data = {
        'CAR_NAME': booking.car.display_name(),
    }
    body = render_to_string("driver_insurance_approved.jade", template_data, Context(autoescape=False))

    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'You have been added to your car\'s insurance',
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
            'TEXT': body,
            'CTA_LABEL': 'Pick up your car',
            'CTA_URL': client_side_routes.bookings(),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject='Alright! Your {} is ready to pick up!'.format(booking.car.display_name()),
        merge_vars=merge_vars,
    )


def insurance_rejected(booking):
    if not booking.driver.email():
        return
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'Sorry, we couldn\'t get you on the insurance.',
            'TEXT': '''
            We didn't manage to get you on the insurance for the car you wanted, but now that your
            account is complete, you can pick another car, and we'll add you to the insurance on that one.
            ''',
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='You counldn\'t be added to the insurance on the car you wanted',
        merge_vars=merge_vars,
    )


def insurance_failed(booking):
    if not booking.driver.email():
        return
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'Sorry, We were unable to complete your booking.',
            'TEXT': '''
            We are sorry to inform you, but we were unable to get you in the {} due to an issue with the owner.
            We ask that you go back to our site and choose another car. We sincerely apologize for any inconvenience.
            '''.format(booking.car.display_name()),
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='We were unable to complete your {} booking'.format(booking.car.display_name()),
        merge_vars=merge_vars,
    )


def car_rented_elsewhere(booking):
    if not booking.driver.email():
        return
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'Sorry, the car you wanted was rented out by someone else.',
            'TEXT': '''
            Sorry, someone else has already rented out the car you wanted. Sometimes that
            happens. Still, there are plenty more great cars available.
            <br/>
            Need help? Contact us:
            support@idlecars.com
            1 844 435 3227
            ''',
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='You counldn\'t be added to the insurance on the car you wanted',
        merge_vars=merge_vars,
    )


def checkout_recipt(booking):
    if not booking.driver.email():
        return
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'HEADLINE': 'Your {} was successfully reserved'.format(booking.car.display_name()),
            'TEXT': '''
            We put a hold on your credit card for the “car” you booked. You will not be charged until you pick up your car.
            ''',
        }
    }
    email.send_async(
        template_name='no_button_no_image',
        subject='Your {} was successfully reserved'.format(booking.car.display_name()),
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
                there are plenty more cars available.'''.format(booking.car.display_name()),
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Someone else rented your {}.'.format(booking.car.display_name()),
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
            'TEXT': body.format(booking.car.display_name()),
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
            'HEADLINE': 'Your account password has been set',
            'TEXT': '''
                If you didn't set your password, or if you think something funny is going
                on, please call us any time at 1-844-IDLECAR (1-844-435-3227).
            ''',
            'CTA_LABEL': 'Find your car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Your idlecars password has been set.',
        merge_vars=merge_vars,
    )


# email for the one-time mailer we send out to legacy users
def account_created(password_reset):
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'HEADLINE': 'An account has been created for you at idlecars.',
            'TEXT': '''
                Your documents and details have been stored in your idlecars account. To claim your
                account just tap the button below. Add a password, and your account  will be secured.
                Then you can rent any car you need, any time you need it.
            ''',
            'CTA_LABEL': 'Claim your account',
            'CTA_URL': client_side_routes.password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='An account has been created for you at idlecars',
        merge_vars=merge_vars,
    )
