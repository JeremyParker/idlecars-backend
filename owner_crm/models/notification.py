# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

from idlecars import email, client_side_routes

from owner_crm.models import Campaign


def _get_payment_params(payment):
    return {
        'payment_amount': payment.amount,
        'payment_invoice_start_time': payment.invoice_start_time,
        'payment_invoice_end_time': payment.invoice_end_time,
        'payment_service_fee': payment.service_fee,
        'payment_status': payment.status,
    }

def _get_booking_params(booking):
    return {
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
    }

def _get_car_params(car):
    return {
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
    }

def _get_owner_params(owner):
    return {
        'owner_email': owner.email(),
        'owner_first_name': owner.first_name(),
        'owner_full_name': owner.name(),
        'owner_phone_number': owner.phone_number(),
    }

def get_merge_vars(context):
    return {
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


class Notification(object):
    def __init__(self, campaign_name, argument):
        self.campaign_name = campaign_name
        self.argument = argument
        self.params = {}

    def argument_class(self):
        return type(self.argument).__name__

    def params_sets(self):
        clas = self.argument_class()

        if clas == 'Driver':
            return [_get_driver_params(self.argument)]

        elif clas == 'Owner':
            return [_get_owner_params(argument)]

        elif clas == 'Booking':
            return [
                _get_booking_params(argument),
                _get_driver_params(argument.driver),
                _get_car_params(argument.car),
                _get_owner_params(argument.car.owner)
            ]

        elif clas == 'Payment':
            return [
                _get_payment_params(argument),
                _get_booking_params(argument.booking),
                _get_driver_params(argument.booking.driver),
                _get_car_params(argument.booking.car),
                _get_owner_params(argument.booking.car.owner)
            ]

    def custom_params_sets(self):
        return []

    def update_params(self, params_sets):
        for params_set in params_sets:
            self.params.update(params_set)

    def get_params(self):
        defaulf_params_sets = self.params_sets()
        customize_params_sets = self.custom_params_sets()

        self.update_params(defaulf_params_sets)
        self.update_params(customize_params_sets)

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
        receiver = self.get_receiver()
        if receiver is None:
            return

        if self.get_channel(receiver) is Campaign.SMS_MEDIUM:
            pass
        else:
            if not receiver['email_address']:
                return

            self.get_params()

            context = self.get_context(**self.params)
            merge_vars = {receiver['email_address']: get_merge_vars(context)}

            email.send_async(
                template_name=context.get('template_name'),
                subject=context.get('subject'),
                merge_vars=merge_vars,
            )


class DriverNotification(Notification):
    def get_receiver(self):
        clas = self.argument_class()

        if clas == 'Driver':
            driver = self.argument
        elif clas == 'Booking':
            driver = self.argument.driver
        elif clas == 'Payment':
            driver = self.argument.booking.driver
        else:
            return None

        return {'email_address': driver.email(), 'sms_enabled': driver.sms_enabled}



class OwnerNotification(Notification):
    def get_all_receivers(self):
        clas = type(self.argument).__name__

        if clas == 'Owner':
            users = self.argument.auth_users.all()
        elif clas == 'Booking':
            users = self.argument.car.owner.auth_users.all()
        elif clas == 'Payment':
            users = self.argument.booking.car.owner.auth_users.all()
        else:
            return []

        # TODO:
        return [{'email_address': user.email, 'sms_enabled': False} for user in users]


class OpsNotification(Notification):
    def get_receiver(self):
        # TODO: get sms_enabled from settings
        return {'email_address': settings.OPS_EMAIL, 'sms_enabled': False}


class StreetTeamNotification(Notification):
    def get_receiver(self):
        # TODO: get sms_enabled from settings
        return {'email_address': settings.STREET_TEAM_EMAIL, 'sms_enabled': False}


