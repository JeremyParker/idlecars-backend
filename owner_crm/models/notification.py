# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from django.core.urlresolvers import reverse

from idlecars import email, client_side_routes

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
        )
    }

def _get_booking_params(booking):
    return {
        'booking': booking,
        'booking_state': booking.get_state(),
        'weekly_rent': booking.weekly_rent,
        'end_time': booking.end_time,
        'checkout_time': booking.checkout_time,
        'requested_time': booking.requested_time,
        'approval_time': booking.approval_time,
        'pickup_time': booking.pickup_time,
        'return_time': booking.return_time,
        'refund_time': booking.refund_time,
        'incomplete_time': booking.incomplete_time,
        'booking_admin_link': 'https://www.idlecars.com{}'.format(
            reverse('admin:server_booking_change', args=(booking.pk,))
        )
    }

def _get_car_params(car):
    return {
        'car': car,
        'car_name': car.display_name(),
        'car_daily_cost': car.quantized_cost(),
        'car_status': car.effective_status(),
        'car_plate': car.plate,
        'car_deposit': car.solo_deposit,
    }

def _get_driver_params(driver):
    return {
        'driver_email': driver.email(),
        'driver_first_name': driver.first_name(),
        'driver_full_name': driver.full_name(),
        'driver_phone_number': driver.phone_number(),
        'driver_license_image': driver.driver_license_image,
        'fhv_license_image': driver.fhv_license_image,
        'address_proof_image': driver.address_proof_image,
        'defensive_cert_image': driver.defensive_cert_image,
        'base_letter': driver.base_letter,
        'driver_admin_link': 'https://www.idlecars.com{}'.format(
            reverse('admin:server_driver_change', args=(driver.pk,))
        ),
    }

def _get_owner_params(owner):
    return {
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
        self.params_sets = []

    def default_params_sets_list(self):
        return {
            'Driver': ['driver'],
            'Owner': ['owner'],
            'Booking': ['booking', 'driver', 'car', 'owner'],
            'Payment': ['booking', 'driver', 'car', 'owner', 'payment'],
            'UserMessage': ['message'],
        }

    def params_match_list(self):
        return {
            'Driver': {
                '_get_driver_params': 'self.argument',
            },
            'Owner': {
                '_get_owner_params': 'self.argument',
            },
            'Booking': {
                '_get_booking_params': 'self.argument',
                '_get_driver_params': 'self.argument.driver',
                '_get_car_params': 'self.argument.car',
                '_get_owner_params': 'self.argument.car.owner',
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
            }
        }

    def get_params(self, sets):
        match_list = self.params_match_list().get(self.argument_class(), {})

        for params_set in sets:
            function_name = '_get_{}_params'.format(params_set)
            argument_name = match_list.get(function_name)
            function = eval(function_name)
            argument = eval(argument_name)
            self.update_params(function(argument))

    def argument_class(self):
        return type(self.argument).__name__ or None

    def default_params_sets(self):
        return self.default_params_sets_list().get(self.argument_class(), [])

    def custom_params_sets(self):
        return []

    def update_params(self, params_set):
        self.params.update(params_set)

    def get_argument_params(self):
        self.params_sets = self.default_params_sets() + self.custom_params_sets()
        self.get_params(self.params_sets)

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
        self.get_argument_params()

        for receiver in self.get_all_receivers():
            if self.get_channel(receiver) is Campaign.SMS_MEDIUM:
                pass
            else:
                if not receiver['email_address']:
                    return

                self.get_receiver_params(receiver)

                context = self.get_context(**self.params)
                merge_vars = {receiver['email_address']: get_merge_vars(context)}

                email.send_async(
                    template_name=context.get('template_name'),
                    subject=context.get('subject'),
                    merge_vars=merge_vars,
                )



class DriverNotification(Notification):
    def get_all_receivers(self):
        clas = self.argument_class()

        if clas == 'Driver':
            driver = self.argument
        elif clas == 'Booking':
            driver = self.argument.driver
        elif clas == 'Payment':
            driver = self.argument.booking.driver
        else:
            return []

        return [{'email_address': driver.email(), 'sms_enabled': driver.sms_enabled}]



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
        else:
            return []

        # TODO:
        return [{'email_address': user.email, 'sms_enabled': False, 'user': user} for user in users]



class OpsNotification(Notification):
    def get_all_receivers(self):
        # TODO: get sms_enabled from settings
        return [{'email_address': settings.OPS_EMAIL, 'sms_enabled': False}]



class StreetTeamNotification(Notification):
    def get_all_receivers(self):
        # TODO: get sms_enabled from settings
        return [{'email_address': settings.STREET_TEAM_EMAIL, 'sms_enabled': False}]
