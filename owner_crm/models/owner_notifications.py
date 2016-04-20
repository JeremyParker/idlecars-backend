# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from decimal import Decimal

# don't import the class or the test will find it and try to test it as a notification.
from django import template
from django.template.loader import render_to_string
from django.conf import settings

from idlecars import email, app_routes_driver, app_routes_owner, fields
from server.services import car as car_service

from owner_crm.models import notification


def _get_car_listing_links(owner):
    links = ''
    for car in car_service.filter_live(owner.cars.all()):
        car_url = app_routes_driver.car_details_url(car)
        links = links + '<li><a href={}>\n\t{}\n</A>\n'.format(car_url, car_url)
    return links


def _render_renewal_body(**kwargs):
    template_data = {
        'CAR_NAME': kwargs['car_name'],
        'CAR_PLATE': kwargs['car_plate'],
    }
    context = template.Context(autoescape=False)
    return render_to_string("car_expiring.jade", template_data, context)


class RenewalEmail(notification.OwnerNotification):
    def get_context(self, **kwargs):
        body = _render_renewal_body(**kwargs)

        context = {
            'FNAME': kwargs.get('user_first_name', None),
            'HEADLINE': 'Your {} listing is about to expire'.format(kwargs['car_name']),
            'TEXT': body,
            'CTA_LABEL': 'Update Listing Now',
            'CTA_URL': kwargs['car_owner_details_url'],
            'CAR_IMAGE_URL': kwargs['car_image_url'],
            'template_name': 'one_button_one_image',
            'subject': 'Your {} listing is about to expire.'.format(kwargs['car_name']),
            'sms_body': 'The listing for your {} with medallion {} is about to expire. \
Is it still available? Please tap here to extend or remove your \
listing: {}'.format(kwargs['car_name'], kwargs['car_plate'], kwargs['car_owner_details_url'])
        }
        return context


class PendingNotification(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = '''Someone is interested in your {} with plates {}. They are still in the process
        of submitting their documents, but we will send you everything as soon as possible. <br /><br />
        If this shift is no longer available, please click below to de-list the shift from our
        marketplace.'''.format(
            kwargs['car_name'],
            kwargs['car_plate'],
        )
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Someone is interested in your {}'.format(kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Delist this shift',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Someone is interested in your {}'.format(kwargs['car_name']),
        }


class SignupConfirmation(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = render_to_string(
            "owner_signup.jade",
            {},
            template.Context(autoescape=False)
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Welcome to All Taxi',
            'TEXT': text,
            'CTA_LABEL': 'Go to your Account',
            'CTA_URL': kwargs['owner_app_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Welcome to your All Taxi owner account',
        }


class NewBookingEmail(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} wants to rent your {} with medallion {}.'.format(
            kwargs['driver_full_name'] or 'A driver',
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        # TODO(JP) track gender of driver and customize this email text
        text = '''
            {} wants to rent your car and has submitted their documentation. If you would like them
            to be added to your insurance policy please see instructions.
            All of their documents are included in this email. If you require any additional
            information for insurance, please reach out to the driver at {}.'''.format(
                kwargs['driver_full_name'] or 'A driver',
                fields.format_phone_number(kwargs['driver_phone_number']),
            )

        context = {
            'PREVIEW': headline,
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': headline,
            'TEXT0': text,
            'IMAGE_1_URL': kwargs['driver_license_image'],
            'TEXT1': 'DMV License <a href="{}">(click here to download)</a>'.format(
                kwargs['driver_license_image']
            ),
            'IMAGE_2_URL': kwargs['fhv_license_image'],
            'TEXT2': 'FHV/Hack License <a href="{}">(click here to download)</a>'.format(
                kwargs['fhv_license_image']
            ),
            'IMAGE_3_URL': kwargs['defensive_cert_image'],
            'TEXT3': 'Defensive Driving Certificate <a href="{}">(click here to download)</a>'.format(
                kwargs['defensive_cert_image']
            ),
            'IMAGE_4_URL': kwargs['address_proof_image'],
            'TEXT4': 'Proof of address <a href="{}">(click here to download)</a>'.format(
                kwargs['address_proof_image']
            ),
            'TEXT5': 'Questions? Need more documentation? Please call {} at {}.'.format(
                    kwargs['driver_first_name'] or 'the driver',
                    fields.format_phone_number(kwargs['driver_phone_number']),
                ),
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'subject': 'A driver has booked your {}.'.format(kwargs['car_name']),
            'template_name': 'one_button_four_images',
            'sms_body': headline + ' An email has been sent to {} with more information.'.format(
                kwargs['user_email']
            )
        }
        return context


class FirstMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = 'Has {} been accepted on the {} with plates {}? Click here to let us \
know: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know if:
        <ul><li> They were accepted on the car’s insurance </li>
            <li> They were rejected by the insurance company </li>
            <li> The car is no longer available </li></ul>'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': sms_body,
        }


class SecondMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = 'Has {} been accepted on the {} with plates {}? Click here to let us \
know: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know if:
        <ul><li> They were accepted on the car’s insurance </li>
            <li> They were rejected by the insurance company </li>
            <li> The car is no longer available </li></ul>'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': sms_body,
        }


class ThirdMorningInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = '{}’s booking of the {} with medallion {} will be cancelled soon. Click below to \
let us know where they are in the process: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know where they
        are in the process, otherwise the booking will be canceled within 24 hours.'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': '{}’s booking will be canceled soon'.format(kwargs['driver_full_name']),
            'sms_body': sms_body,
        }


class FirstAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = 'Has {} been accepted on the {} with plates {}? Click here to let us \
know: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know if:
        <ul><li> They were accepted on the car’s insurance </li>
            <li> They were rejected by the insurance company </li>
            <li> The car is no longer available </li></ul>'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': sms_body,
        }

class SecondAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = 'Has {} been accepted on the {} with plates {}? Click here to let us \
know: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know if:
        <ul><li> They were accepted on the car’s insurance </li>
            <li> They were rejected by the insurance company </li>
            <li> The car is no longer available </li></ul>'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'sms_body': sms_body,
        }


class ThirdAfternoonInsuranceReminder(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = '{}’s booking of the {} with medallion {} will be cancelled soon. Click here to let \
us know where they are in the process: {}'.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
            kwargs['car_owner_details_url']
        )
        text = '''Has {} been accepted on the {}? Click the button below to let us know where they
        are in the process, otherwise the booking will be canceled within 24 hours.'''.format(
            kwargs['driver_full_name'],
            kwargs['car_name'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has {} been accepted on the {}?'.format(kwargs['driver_full_name'], kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Accept/Reject Diver',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': '{}’s booking will be canceled soon'.format(kwargs['driver_full_name']),
            'sms_body': sms_body,
        }


class BookingCanceled(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has decided not to rent your {}, with medallion {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = 'We\'re sorry. {} has decided not to rent your {}. Could you ask your insurance \
broker not to add them to the insurance policy? We apologise for any inconvenience. We\'ve \
already re-listed your car on the site so we can find you another driver as soon as possible.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        # TODO(JP) track gender of driver and customize this email text
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': kwargs['car_driver_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your {} rental has canceled.'.format(kwargs['car_name']),
            'sms_body': text,
        }


class DriverRejected(notification.OwnerNotification):
    def get_context(self, **kwargs):
        headline = '{} has decided not to rent your {}, with medallion {}'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
            kwargs['car_plate'],
        )

        text = 'We\'re sorry. {} has decided not to rent your {}. We apologise for any inconvenience. \
We\'ve already re-listed your car on the site so we can find you another driver as soon as possible.'.format(
            kwargs['driver_first_name'],
            kwargs['car_name'],
        )
        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': headline,
            'TEXT': text,
            'CTA_LABEL': 'See your listing',
            'CTA_URL': kwargs['car_driver_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Your {} rental has canceled.'.format(kwargs['car_name']),
            'sms_body': text,
        }


class InsuranceTooSlow(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Your {} rental has been canceled'.format(kwargs['car_name']),
            'TEXT': '''
                We are sorry to inform you, but we cancelled the {} rental for {}.
                We require drivers get on the insurance and into cars within 24 to 48 hours,
                so we hope that we will be able to do this next time.
                <br />
                If you are unsatisfied with your broker - please contact us to be added to our preferred broker list.
            '''.format(kwargs['car_name'], kwargs['driver_full_name']),
            'template_name': 'no_button_no_image',
            'subject': 'Your {} rental has been canceled'.format(kwargs['car_name']),
        }


class ConfirmReturned(notification.OwnerNotification):
    def get_context(self, **kwargs):
        sms_body = '{} says your car has been returned. Please click {} to confirm and refund \
any deposit to the driver'.format(kwargs['car_name'], kwargs['car_owner_details_url'])
        text = '''{} says your car has been returned. Please click below to confirm that the car \
        has been returned in good condition, and refund the driver\'s deposit. If your car has not been \
        returned, or if there is a problem, please contact the driver at {}'''.format(
            kwargs['driver_full_name'],
            kwargs['driver_phone_number'],
        )

        return {
            'FNAME': kwargs['user_first_name'] or None,
            'HEADLINE': 'Has your {} been returned?'.format(kwargs['car_name']),
            'TEXT': text,
            'CTA_LABEL': 'Confirm and refund any deposit',
            'CTA_URL': kwargs['car_owner_details_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Has your {} been returned?'.format(kwargs['car_name']),
            'sms_body': sms_body,
        }


class AccountCreated(notification.OwnerNotification):
    def get_context(self, **kwargs):
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'CTA_URL': kwargs['owner_password_reset_url'],
            'template_name': 'owner_account_invite',
            'subject': 'Complete your account today - sign up with your bank account and start getting paid',
        }


class PasswordReset(notification.OwnerNotification):
    def get_context(self, **kwargs):
        text = 'We\'ve received a request to reset your password. If you didn\'t make the request, just \
ignore this message. Otherwise, you can reset your password using this link: '
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Reset your password',
            'TEXT': text,
            'CTA_LABEL': 'Reset password',
            'CTA_URL': kwargs['owner_password_reset_url'],
            'template_name': 'one_button_no_image',
            'subject': 'Reset your idlecars password.',
            'sms_body': text + kwargs['owner_password_reset_url'],
        }


class PasswordResetConfirmation(notification.OwnerNotification):
    def get_context(self, **kwargs):
        subject = 'Your idlecars password has been set.'
        text = 'If you didn\'t set your password, or if you think something funny is going \
on, please call us any time at ' + settings.IDLECARS_PHONE_NUMBER + '.'
        return {
            'FNAME': kwargs['password_reset_user_first_name'] or None,
            'HEADLINE': 'Your account password has been set',
            'TEXT': text,
            'CTA_LABEL': 'Find your car',
            'CTA_URL': kwargs['car_listing_url'],
            'template_name': 'one_button_no_image',
            'subject': subject,
            'sms_body': subject + ' ' + text,
        }


class BankAccountApproved(notification.OwnerNotification):
    def get_context(self, **kwargs):
        links = _get_car_listing_links(kwargs['owner'])
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
                '''

        return {
            'FNAME': kwargs['user_first_name'],
            'HEADLINE': 'Your bank account has been approved',
            'TEXT': text,
            'CTA_LABEL': 'List more cars',
            'CTA_URL': app_routes_owner.owner_app_url(),
            'template_name': 'one_button_no_image',
            'subject': 'Your bank account has been approved.',
        }
