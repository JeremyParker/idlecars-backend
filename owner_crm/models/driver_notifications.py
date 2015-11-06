# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, client_side_routes

from server.services import car as car_service

from owner_crm.models import notification


class DocsApprovedNoBooking(notification.DriverNotification):
    def get_context(self, **kwargs):
        subject = 'Welcome to idlecars, {driver_full_name}!'.format(**kwargs)
        headline = 'Your documents have been reviewed and approved.'
        text = 'You are now ready to rent any car on idlecars with one tap!'
        cta_url = client_side_routes.car_listing_url()

        return {
            'FNAME': kwargs['driver_email'],
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'Rent a car now',
            'CTA_URL': cta_url,
            'subject': subject,
            'template_name': 'one_button_no_image',
            'sms_body': subject + ' ' + headline + ' ' + text + ' Click here to rent a car now: ' + cta_url
        }



class BaseLetterApprovedNoCheckout(notification.DriverNotification):
    def get_context(self, **kwargs):
        template_data = {'CAR_NAME': kwargs['car_name']}
        body = render_to_string("base_letter_approved_no_checkout.jade", template_data, Context(autoescape=False))

        return {
            # TODO: I think we don't need `or None` because it return '', and '' looks the same as None to drivers
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body,
            'CTA_LABEL': 'Reserve now',
            'CTA_URL': client_side_routes.bookings(),
            'HEADLINE': 'Your {} is waiting'.format(kwargs['car_name']),
            'CAR_IMAGE_URL': car_service.get_image_url(kwargs['car']),
            'template_name': 'one_button_no_image',
            'subject': 'Your {} is waiting on your payment information!'.format(kwargs['car_name']),
        }


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

    # TODO: We should pass the booking that we're notifying about in with
    # the function call. This logic can exist upstream for reminder emails.
    from server.services import booking as booking_service
    pending_bookings = booking_service.filter_pending(driver.booking_set)

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
        'Are you ready to drive?'
    ]
    body_template = [
        'third_docs_reminder_booking.jade',
        'second_docs_reminder_driver.jade'
    ]

    documents_reminder(driver, subject, body_template)


def booking_timed_out(booking):
    if not booking.driver.email():
        return

    if booking.driver.all_docs_uploaded():
        template = 'booking_timed_out_cc.jade'
        subject = 'Your {} booking has been cancelled because you never checked out.'.format(
            booking.car.display_name()
        )
    else:
        template = 'booking_timed_out.jade'
        subject = 'Your booking has been cancelled because we don\'t have your driver documents.'

    template_data = {
        'CAR_NAME': booking.car.display_name(),
    }
    merge_vars = {
        booking.driver.email(): {
            'FNAME': booking.driver.first_name() or None,
            'TEXT': render_to_string(template, template_data, Context(autoescape=False)),
            'CTA_LABEL': 'Find your car',
            'CTA_URL': client_side_routes.car_listing_url(),
            'HEADLINE': 'Your {} rental was canceled'.format(booking.car.display_name()),
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject=subject,
        merge_vars=merge_vars,
    )


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
            'CTA_LABEL': 'See your rental',
            'CTA_URL': client_side_routes.bookings(),
            'HEADLINE': 'Your documents have been reviewed and approved',
            'CAR_IMAGE_URL': car_service.get_image_url(booking.car),
        }
    }
    email.send_async(
        template_name='one_button_one_image',
        subject='Congratulations! Your documents have been submitted!',
        merge_vars=merge_vars,
    )


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
        subject='You couldn\'t be added to the insurance on the car you wanted',
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
            <br />
            <p>Need help? Contact us:</p>
            <p>support@idlecars.com </p>
            <p>''' + settings.IDLECARS_PHONE_NUMBER + '</p>',
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': client_side_routes.car_listing_url(),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='Sorry, someone else rented out the car you wanted.',
        merge_vars=merge_vars,
    )


class CheckoutReceipt(notification.DriverNotification):
    def get_context(self, **kwargs):
        from server.services import booking as booking_service
        first_rental_payment = booking_service.estimate_next_rent_payment(kwargs['booking'])[1]

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Your {} was successfully reserved'.format(kwargs['car_name']),
            'TEXT': '''
            We put a hold of ${} on your credit card for the {} you booked. You will not be charged until
            you inspect, approve, and pick up your car. Once you approve the car in the app, the hold on
            your card will be processed, and your card will be charged for the first rental payment of ${}.
            '''.format(
                kwargs['car_deposit'],
                kwargs['car_name'],
                first_rental_payment,
            ),
            'template_name': 'no_button_no_image',
            'subject': 'Your {} was successfully reserved'.format(kwargs['car_name']),
        }


class PickupConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'You are ready to drive!',
            'TEXT': '''
                Success! Your card has been charged {} for the {} booking.
                The owner should receive an email that the payment was processed and should give you the keys to start driving.
                <br />
                Please contact us if there are any issues.
            '''.format(kwargs['booking_weekly_rent'], kwargs['car_name']),
            'template_name': 'no_button_no_image',
            'subject': 'You are ready to drive!',
        }


class PaymentReceipt(notification.DriverNotification):
    def get_context(self, **kwargs):
        text = '''
            Your weekly rental fee has been paid. <br />
            Driver: {} <br />
            Car: {} <br /><br />

            Invoice Period: {} - {} <br />
            Payment Amount: {} <br /><br />
        '''
        from server.services import booking as booking_service
        fee, amount, start_time, end_time = booking_service.calculate_next_rent_payment(kwargs['booking'])
        if amount > 0:
            text += 'Your next payment of ${} will occur on {} <br />'.format(amount, end_time.strftime('%b %d'))
        else:
            text += 'This is your last payment. <br />'

        text += 'Your booking will end on {}. <br /><br />Thank you for using idlecars.'
        text = text.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['payment_invoice_start_time'].strftime('%b %d'),
            kwargs['payment_invoice_end_time'].strftime('%b %d'),
            kwargs['payment_amount'],
            kwargs['booking_end_time'].strftime('%b %d'),
        )

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Payment Received: {} Booking'.format(kwargs['car_name']),
            'TEXT': text,
            'template_name': 'no_button_no_image',
            'subject': 'Payment Received: {} Booking'.format(kwargs['car_name']),
        }


class SomeoneElseBooked(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'HEADLINE': 'Someone else rented your car!',
            'TEXT': '''While we were waiting for you to finish uploading your documents,
                another driver rented your car. But don't worry,
                there are plenty more cars available.'''.format(kwargs['car_name']),
            'CTA_LABEL': 'Find a new car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Someone else rented your {}.'.format(kwargs['car_name']),
        }


class BookingCanceled(notification.DriverNotification):
    def get_context(self, **kwargs):
        body = '''
            Your {} rental has been canceled. Now you can go back to idlecars and rent another car!
        '''

        return {
            'FNAME': kwargs['driver_first_name'] or None,
            'TEXT': body.format(kwargs['car_name']),
            'CTA_LABEL': 'Find another car',
            'CTA_URL': kwargs['car_listing_url'],
            'HEADLINE': 'Your rental has been canceled',
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Confirmation: Your rental has been canceled.',
        }


class PasswordReset(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Reset your password',
            'TEXT': '''
            We've received a request to reset your password.
            If you didn't make the request, just ignore this email.
            Otherwise, you can reset your password using this link:''',
            'CTA_LABEL': 'Reset password',
            'CTA_URL': kwargs['password_reset_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Reset your password on idlecars.',
        }


class PasswordResetConfirmation(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Your account password has been set',
            'TEXT': '''
                If you didn't set your password, or if you think something funny is going
                on, please call us any time at ''' + settings.IDLECARS_PHONE_NUMBER + '.',
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your idlecars password has been set.',
        }


# email for the one-time mailer we send out to legacy users
class AccountCreated(notification.DriverNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'An account has been created for you at idlecars.',
            'TEXT': '''
                Your documents and details have been stored in your idlecars account. To claim your
                account just tap the button below. Add a password, and your account  will be secured.
                Then you can rent any car you need, any time you need it.
            ''',
            'CTA_LABEL': 'Claim your account',
            'CTA_URL': kwargs['password_reset_url'],
            'template_name': 'one_button_no_image',
            'subject': 'An account has been created for you at idlecars',
        }
