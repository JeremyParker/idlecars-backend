# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse

from idlecars import email, client_side_routes, sms_service
from server.services import car as car_service
from owner_crm.models import Campaign


def _get_payment_params(payment):
    return {
        'payment': payment,
        'payment_amount': payment.amount,
        'payment_invoice_description': payment.invoice_description(),
        'payment_invoice_start_time': payment.invoice_start_time,
        'payment_invoice_end_time': payment.invoice_end_time,
        'payment_service_fee': payment.service_fee,
        'payment_status': payment.status,
        'payment_notes': payment.notes,
        'payment_admin_link': 'https://www.idlecars.com{}'.format(
            reverse('admin:server_payment_change', args=(payment.pk,))
        ),
    }

def _get_booking_params(booking):
    from server.services import booking as booking_service
    if booking.pickup_time:
        (
            booking_payment_fee,
            next_payment_amount,
            invoice_start_time,
            invoice_end_time
        ) = booking_service.calculate_next_rent_payment(booking)
    else:
        (
            booking_payment_fee,
            next_payment_amount,
            invoice_start_time,
            invoice_end_time
        ) = booking_service.estimate_next_rent_payment(booking)

    return {
        'booking_state': booking.get_state(),
        'booking_weekly_rent': booking.weekly_rent,
        'booking_end_time': booking.end_time,
        'booking_checkout_time': booking.checkout_time,
        'booking_requested_time': booking.requested_time,
        'booking_approval_time': booking.approval_time,
        'booking_pickup_time': booking.pickup_time,
        'booking_return_time': booking.return_time,
        'booking_refund_time': booking.refund_time,
        'booking_incomplete_time': booking.incomplete_time,
        'booking_admin_link': 'https://www.idlecars.com{}'.format(
            reverse('admin:server_booking_change', args=(booking.pk,))
        ),
        'booking_next_payment_amount': next_payment_amount,
        'booking_payment_fee': booking_payment_fee,
        'booking_invoice_start_time': invoice_start_time,
        'booking_invoice_end_time': invoice_end_time,
    }

def _get_car_params(car):
    return {
        'car_name': car.display_name(),
        'car_daily_cost': car.quantized_cost(),
        'car_status': car.effective_status(),
        'car_plate': car.plate,
        'car_deposit': car.solo_deposit,
        'car_image_url': car_service.get_image_url(car),
        'car_details_url': client_side_routes.car_details_url(car)
    }


# helper for _get_driver_params
def _missing_documents_html(driver):
    from server.services import driver as driver_service
    doc_names = driver_service.get_missing_docs(driver)
    if not doc_names:
        return ''

    docs = ''
    for name in doc_names[:-1]:
        docs = docs + '<li>' + name + ', '
    if docs:
        docs = docs + 'and'
    docs = docs + '<li>' + doc_names[-1]
    return docs


def _get_driver_params(driver):
    from server.services import driver as driver_service
    return {
        'driver': driver,
        'driver_email': driver.email(),
        'driver_first_name': driver.first_name(),
        'driver_full_name': driver.full_name(),
        'driver_phone_number': driver.phone_number(),
        'driver_all_docs_uploaded': driver.all_docs_uploaded(),
        'driver_license_image': driver.driver_license_image,
        'fhv_license_image': driver.fhv_license_image,
        'address_proof_image': driver.address_proof_image,
        'defensive_cert_image': driver.defensive_cert_image,
        'base_letter': driver.base_letter,
        'driver_admin_link': 'https://www.idlecars.com{}'.format(
            reverse('admin:server_driver_change', args=(driver.pk,))
        ),
        'missing_docs_list': ', '.join(driver_service.get_missing_docs(driver)),
        'missing_docs_html': _missing_documents_html(driver),
    }


def _get_owner_params(owner):
    return {
        'owner': owner,
        'owner_email': owner.email(),
        'owner_name': owner.name(),
        'owner_first_name': owner.first_name(),
        'owner_phone_number': owner.phone_number(),
    }

def _get_user_params(user):
    return {
        'user_first_name': user.first_name,
        'user_phone_number': user.username,
        'user_email': user.email,
    }

def _get_message_params(message):
    return {
        'message_first_name': message.first_name,
        'message_body': message.message,
        'message_email': message.email,
    }

def _get_renewal_params(renewal):
    return {
        'renewal_url': client_side_routes.renewal_url(renewal),
    }

def _get_password_reset_params(password_reset):
    return {
        'password_reset_user_first_name': password_reset.auth_user.first_name,
        'password_reset_url': client_side_routes.password_reset(password_reset),
        'password_owner_reset_url': client_side_routes.owner_password_reset(password_reset),
    }

def _get_urls_params(pseudo_argument):
    return {
        'car_listing_url': client_side_routes.car_listing_url(),
        'docs_upload_url': client_side_routes.doc_upload_url(),
        'bookings_url': client_side_routes.bookings(),
        'driver_account_url': client_side_routes.driver_account(),
        'terms_of_service_url': client_side_routes.terms_of_service(),
        'faq_url': client_side_routes.faq(),
        'add_car_form_url': client_side_routes.add_car_form(),
    }


def get_merge_vars(context):
    merge_vars_origin = {
        'PREVIEW': context.get('PREVIEW'),
        'FNAME': context.get('FNAME'),
        'HEADLINE': context.get('HEADLINE'),
        'TEXT': context.get('TEXT'),
        'TEXT0': context.get('TEXT0'),
        'TEXT1': context.get('TEXT1'),
        'TEXT2': context.get('TEXT2'),
        'TEXT3': context.get('TEXT3'),
        'TEXT4': context.get('TEXT4'),
        'TEXT5': context.get('TEXT5'),
        'TEXT6': context.get('TEXT6'),
        'IMAGE_1_URL': context.get('IMAGE_1_URL'),
        'IMAGE_2_URL': context.get('IMAGE_2_URL'),
        'IMAGE_3_URL': context.get('IMAGE_3_URL'),
        'IMAGE_4_URL': context.get('IMAGE_4_URL'),
        'IMAGE_5_URL': context.get('IMAGE_5_URL'),
        'CTA_LABEL': context.get('CTA_LABEL'),
        'CTA_URL': context.get('CTA_URL'),
        'CAR_IMAGE_URL': context.get('CAR_IMAGE_URL'),
    }

    merge_vars = {}
    merge_vars.update((key, val) for key, val in merge_vars_origin.iteritems() if val is not None)

    return merge_vars


class Notification(object):
    def __init__(self, campaign_name, argument):
        self.campaign_name = campaign_name
        self.argument = argument
        self.params = {}

    def get_params(self, sets):
        match_list = {
            'Driver': {
                '_get_driver_params': 'self.argument',
                '_get_urls_params': 'None',
            },
            'Owner': {
                '_get_owner_params': 'self.argument',
            },
            'Booking': {
                '_get_booking_params': 'self.argument',
                '_get_driver_params': 'self.argument.driver',
                '_get_car_params': 'self.argument.car',
                '_get_owner_params': 'self.argument.car.owner',
                '_get_urls_params': 'None',
            },
            'Payment': {
                '_get_payment_params': 'self.argument',
                '_get_booking_params': 'self.argument.booking',
                '_get_driver_params': 'self.argument.booking.driver',
                '_get_car_params': 'self.argument.booking.car',
                '_get_owner_params': 'self.argument.booking.car.owner',
            },
            'UserMessage': {
                '_get_message_params': 'self.argument',
            },
            'Renewal': {
                '_get_renewal_params': 'self.argument',
                '_get_car_params': 'self.argument.car',
                '_get_owner_params': 'self.argument.car.owner',
            },
            'PasswordReset': {
                '_get_password_reset_params': 'self.argument',
                '_get_urls_params': 'None',
            }
        }.get(self.argument_class(), {})

        for params_set in sets:
            function_name = '_get_{}_params'.format(params_set)
            argument_name = match_list.get(function_name)
            function = eval(function_name)
            argument = eval(argument_name)
            self.update_params(function(argument))

    def argument_class(self):
        return type(self.argument).__name__ or None

    def default_params_sets(self):
        return {
            'Driver': ['driver', 'urls'],
            'Owner': ['owner'],
            'Booking': ['booking', 'driver', 'car', 'owner', 'urls'],
            'Payment': ['booking', 'driver', 'car', 'owner', 'payment'],
            'UserMessage': ['message'],
            'Renewal': ['renewal', 'car', 'owner'],
            'PasswordReset': ['password_reset', 'urls'],
        }.get(self.argument_class(), [])

    def custom_params_sets(self):
        return []

    def update_params(self, params_set):
        self.params.update(params_set)

    def get_receiver_params(self, receiver):
        pass

    def get_channel(self, receiver):
        try:
            campaign = Campaign.objects.get(name=self.campaign_name)
        except Campaign.DoesNotExist:
            campaign = Campaign.objects.create(name=self.campaign_name)

        if campaign.preferred_medium is Campaign.SMS_MEDIUM and receiver['sms_enabled']:
            return Campaign.SMS_MEDIUM
        else:
            return Campaign.EMAIL_MEDIUM

    def send(self):
        self.get_params(self.default_params_sets() + self.custom_params_sets())

        for receiver in self.get_all_receivers():
            self.get_receiver_params(receiver)
            context = self.get_context(**self.params)

            if self.get_channel(receiver) is Campaign.SMS_MEDIUM:
                if not receiver['phone_number']:
                    continue
                phone_number = '+1{}'.format(receiver['phone_number'])
                body = context['sms_body']
                sms_service.send_async(to=phone_number, body=body)
            elif self.get_channel(receiver) is Campaign.EMAIL_MEDIUM:
                if not receiver['email_address']:
                    continue

                merge_vars = {receiver['email_address']: get_merge_vars(context)}

                email.send_async(
                    template_name=context.get('template_name'),
                    subject=context.get('subject'),
                    merge_vars=merge_vars,
                )
            else:
                assert(False)  # programming error. Medium should be SMS or EMAIL


class DriverNotification(Notification):
    def get_all_receivers(self):
        clas = self.argument_class()

        if clas == 'Driver':
            driver = self.argument
        elif clas == 'Booking':
            driver = self.argument.driver
        elif clas == 'Payment':
            driver = self.argument.booking.driver
        elif clas == 'PasswordReset':
            driver = self.argument.auth_user
            return [{
                'email_address': driver.email,
                'phone_number': driver.username,
                'sms_enabled': False,
            }]
        else:
            return []

        return [{
            'email_address': driver.email(),
            'phone_number': driver.phone_number(),
            'sms_enabled': driver.sms_enabled,
        }]


class OwnerNotification(Notification):
    def get_receiver_params(self, receiver):
        receiver = receiver['user']
        receiver_params = _get_user_params(receiver)
        self.update_params(receiver_params)

    def get_all_receivers(self):
        clas = self.argument_class()

        if clas == 'Owner':
            users = self.argument.auth_users.all()
        elif clas == 'Booking':
            users = self.argument.car.owner.auth_users.all()
        elif clas == 'Payment':
            users = self.argument.booking.car.owner.auth_users.all()
        elif clas == 'Renewal':
            users = self.argument.car.owner.auth_users.all()
        elif clas == 'PasswordReset':
            users = [self.argument.auth_user]
        else:
            return []

        # TODO: consider having a "primary contact" or something.
        return [{
                'email_address': user.email,
                'phone_number': user.username,
                'sms_enabled': False,
                'user': user
            } for user in users]


class OpsNotification(Notification):
    def get_all_receivers(self):
        return [{
            'email_address': settings.OPS_EMAIL,
            'phone_number': settings.OPS_PHONE_NUMBER,
            'sms_enabled': True
        }]


class StreetTeamNotification(Notification):
    def get_all_receivers(self):
        return [{'email_address': settings.STREET_TEAM_EMAIL, 'sms_enabled': False}]
