# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.template import Context
from django.template.loader import render_to_string

from idlecars import email, client_side_routes
from server.services import car as car_service


def _get_car_listing_links(owner):
    links = ''
    for car in car_service.filter_live(owner.cars.all()):
        car_url = client_side_routes.car_details_url(car)
        links = links + '<li><a href={}>\n\t{}\n</A>\n'.format(car_url, car_url)
    return links


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

    for user in car.owner.auth_users.all():
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

    for user in booking.car.owner.auth_users.all():
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


def _booking_incomplete_email(booking, body_text):
    headline = '{} has decided not to rent your {}, with license plate {}'.format(
        booking.driver.full_name(),
        booking.car.display_name(),
        booking.car.plate,
    )
    subject = 'Your {} booking has canceled.'.format(booking.car.display_name())
    for user in booking.car.owner.auth_users.all():
        if not user.email:
            continue
        merge_vars = {
            user.email: {
                'FNAME': user.first_name or None,
                'HEADLINE': subject,
                'TEXT': body_text,
                'CTA_LABEL': 'See your listing',
                'CTA_URL': client_side_routes.car_details_url(booking.car)
            }
        }
        email.send_async(
            template_name='one_button_no_image',
            subject=subject,
            merge_vars=merge_vars,
        )


def booking_canceled(booking):
    # TODO(JP) track gender of driver and customize this email text
    text = '''We're sorry. {} has decided not to rent your {}. Could you ask your insurance
    broker not to add them to the insurance policy? We apologise for any inconvenience. We've
    already re-listed your car on the site so we can find you another driver as soon as possible.
    '''.format(
        booking.driver.first_name(),
        booking.car.display_name(),
    )
    _booking_incomplete_email(booking, text)


def driver_rejected(booking):
    text = '''We're sorry. {} has decided not to rent your {}. We apologise for any inconvenience.
    We've already re-listed your car on the site so we can find you another driver as soon as possible.
    '''.format(
        booking.driver.first_name(),
        booking.car.display_name(),
    )
    _booking_incomplete_email(booking, text)


def insurance_follow_up_email(booking):
    # TODO(JP)
    pass


def first_rent_payment(booking):
    pass


def account_created(password_reset):
    if not password_reset.auth_user.email:
        return  # TODO - send some sort of error email, or at least log the error.
    merge_vars = {
        password_reset.auth_user.email: {
            'FNAME': password_reset.auth_user.first_name or None,
            'CTA_URL': client_side_routes.owner_password_reset(password_reset),
        }
    }
    email.send_async(
        template_name='owner_account_invite',
        subject='Welcome to Idle Cars - complete your owner account, so you can get paid',
        merge_vars=merge_vars,
    )


def bank_account_approved(owner):
    links = _get_car_listing_links(owner)
    if links:
        text = '''
                Congrats! Your bank information has been approved and your cars have been listed!
                You can view your live cars from the links below!
                <ul>{}</ul>
                If you have any other cars you would like to list, please go to the submission form here:
            '''.format(links)
    else:
        text = '''
                Congrats! Your bank information has been approved! Now when you rent cars through idlecars, you will
                receive payment directly from the driver into your bank account.<br>
                If you have any cars you would like to list, please go to the submission form here:
            '''.format(links)

    for auth_user in owner.auth_users.all():
        if not auth_user.email:
            continue
        merge_vars = {
            auth_user.email: {
                'FNAME': auth_user.first_name,
                'HEADLINE': 'Your bank account has been approved',
                'TEXT': text,
            'CTA_LABEL': 'List more cars',
            'CTA_URL': client_side_routes.add_car_form(),
            }
        }
        email.send_async(
            template_name='one_button_no_image',
            subject='Your bank account has been approved.',
            merge_vars=merge_vars,
        )
