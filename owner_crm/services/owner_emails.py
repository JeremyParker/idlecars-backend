# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes
from server.services import car as car_service


def _render_renewal_body(car):
    template_data = {
        'CAR_NAME': car.display_name(),
        'CAR_PLATE': car.plate,
    }
    context = Context(autoescape=False)
    return render_to_string("car_expiring.jade", template_data, context)


def renewal_email(car, renewal):
    renewal_url = client_side_routes.renewal_url(renewal)
    body = _render_renewal_body(car)
    car_desc = car.display_name()

    for user in car.owner.user_account.all():
        if not user.email:
            continue
        merge_vars = {
            user.email: {
                'FNAME': user.first_name or None,
                'HEADLINE': 'Your {} listing is about to expire'.format(car_desc),
                'TEXT': body,
                'CTA_LABEL': 'Renew Listing Now',
                'CTA_URL': renewal_url,
                'CAR_IMAGE_URL': car_service.get_image_url(car),
            }
        }
        email.send_async(
            template_name='one_button_one_image',
            subject='Your {} listing is about to expire.'.format(car_desc),
            merge_vars=merge_vars,
        )


def new_booking_email(booking):
    headline = '{} has booked your {}, with license plate {}'.format(
        booking.driver.full_name(),
        booking.car.display_name(),
        booking.car.plate,
    )

    # TODO(JP) track gender of driver and customize this email text
    text = '''All of {}\'s required documentation is included in this email.
    Please have him added to the insurance policy today to ensure
    they are able to start driving tomorrow.'''.format(booking.driver.first_name())

    for user in booking.car.owner.user_account.all():
        if not user.email:
            continue
        merge_vars = {
            booking.car.owner.email(): {
                'PREVIEW': headline,
                'FNAME': user.first_name,
                'HEADLINE': headline,
                'TEXT0': text,
                'IMAGE_1_URL': booking.driver.driver_license_image,
                'TEXT1': 'DMV License <a href="{}">(click here to download)</a>'.format(
                    booking.driver.driver_license_image
                ),
                'IMAGE_2_URL': booking.driver.fhv_license_image,
                'TEXT2': 'FHV/Hack License <a href="{}">(click here to download)</a>'.format(
                    booking.driver.fhv_license_image
                ),
                'IMAGE_3_URL': booking.driver.defensive_cert_image,
                'TEXT3': 'Defensive Driving Certificate <a href="{}">(click here to download)</a>'.format(
                    booking.driver.defensive_cert_image
                ),
                'IMAGE_4_URL': booking.driver.address_proof_image,
                'TEXT4': 'Proof of address <a href="{}">(click here to download)</a>'.format(
                    booking.driver.address_proof_image
                ),
                'TEXT5': 'Questions? Call us at 1-844-IDLECAR (1-844-435-3227)',
            }
        }
        email.send_async(
            template_name='no_button_four_images',
            subject='A driver has booked your {}.'.format(booking.car.display_name()),
            merge_vars=merge_vars,
        )


def booking_canceled(booking):
    headline = '{} has decided not to rent your {}, with license plate {}'.format(
        booking.driver.full_name(),
        booking.car.display_name(),
        booking.car.plate,
    )

    # TODO(JP) track gender of driver and customize this email text
    text = '''We're sorry. {} has decided not to rent your {}. Could you ask your insurance
    broker not to add them to the insurance policy? We apologise for any inconvenience. We've
    already re-listed your car on the site so we can find you another driver as soon as possible.
    '''.format(
        booking.driver.first_name(),
        booking.car.display_name(),
    )
    subject = 'Your {} booking has canceled.'.format(booking.car.display_name())
    for user in booking.car.owner.user_account.all():
        if not user.email:
            continue
        merge_vars = {
            user.email: {
                'FNAME': user.first_name or None,
                'HEADLINE': subject,
                'TEXT': text,
                'CTA_LABEL': 'See your listing',
                'CTA_URL': client_side_routes.car_details_url(booking.car)
            }
        }
        email.send_async(
            template_name='one_button_no_image',
            subject=subject,
            merge_vars=merge_vars,
        )


def insurance_follow_up_email(booking):
    # TODO(JP)
    pass


def account_created(password_reset):
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'HEADLINE': 'An account has been created for you at idlecars.',
            'TEXT': '''
            Your car(s) are ready to be listed on the idlecars marketplace. Please click below
            to secure your account with a password, and link your bank account to get paid.
            ''',
            'CTA_LABEL': 'Link your account',
            'CTA_URL': client_side_routes.owner_password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='one_button_no_image',
        subject='An account has been created for you at idlecars',
        merge_vars=merge_vars,
    )
