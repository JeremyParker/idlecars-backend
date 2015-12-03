# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ChoiceField

from idlecars import app_routes_driver, fields
from server.models import Car, Owner
from server.fields import CarColorField
from server.services import car_helpers, booking as booking_service


class CarCreateSerializer(ModelSerializer):
    name = SerializerMethodField()
    state_string = SerializerMethodField()
    state_buttons = SerializerMethodField()
    insurance = SerializerMethodField()
    listing_link = SerializerMethodField()
    available_date_display = SerializerMethodField()
    min_lease_display = SerializerMethodField()

    next_available_date = fields.DateArrayField(required=False, allow_null=True,)
    interior_color = CarColorField(required=False, allow_null=True,)
    exterior_color = CarColorField(required=False, allow_null=True,)

    class Meta:
        model = Car
        fields = (
            'created_time',
            'id',
            'name',
            'plate',
            'owner',
            'base',
            'state_string',
            'state_buttons',
            'insurance',
            'listing_link',

            'solo_cost',
            'solo_deposit',
            'next_available_date',
            'available_date_display',
            'min_lease',
            'min_lease_display',
            'exterior_color',
            'interior_color',
            'last_known_mileage',
        )
        read_only_fields = (
            'id',
            'name',
            'created_time',
            'state',
            'listing_link',
            'available_date_display',
            'state_string',
            'state_buttons',
            'min_lease_display',
            # fields we get from the TLC
            'make_model',
            'year',
            'base',
            'insurance',
       )

    def get_name(self, obj):
        if not obj.make_model:
            return '{} Unknown Car'.format(obj.year)
        return '{} {}'.format(obj.year, obj.make_model)

    def get_state_string(self, obj):
        return self._get_state_values(obj)['state_string']

    def get_state_buttons(self, obj):
        return self._get_state_values(obj)['buttons']

    def get_insurance(self, obj):
        if obj.insurance:
            return obj.insurance.insurer_name
        return None

    def get_listing_link(self, obj):
        return app_routes_driver.car_details_url(obj)

    def get_available_date_display(self, obj):
        if not obj.next_available_date:
            return 'Unavailable'
        elif obj.next_available_date > timezone.now():
            return obj.next_available_date.strftime('%b %d')
        else:
            return 'Immediately'

    def _get_state_values(self, car):
        if not car_helpers.is_data_complete(car):
            return {
                'state_string': 'Waiting for information',
                'buttons': [{
                    'label': 'Complete this listing',
                    'function_key': 'GoRequiredField',
                }]
            }
        elif car.status == Car.STATUS_BUSY:
            if car.next_available_date:
                return {
                    'state_string': 'Busy until {}'.format(car.next_available_date.strftime('%b %d')),
                    'buttons': [{
                        'label': 'Change available date',
                        'function_key': 'GoNextAvailableDate',
                    }]
                }
            else:
                return {
                    'state_string': 'Not listed',
                    'buttons': [{
                        'label': 'Relist',
                        'function_key': 'GoNextAvailableDate',
                    }]
                }
        elif car.owner and not car.owner.merchant_account_state or \
            car.owner.merchant_account_state == Owner.BANK_ACCOUNT_DECLINED:
            return {
                'state_string': 'Waiting for direct deposit information',
                'buttons': [{
                    'label': 'Add bank details',
                    'function_key': 'AddBankLink',
                }]
            }
        elif car.owner and car.owner.merchant_account_state == Owner.BANK_ACCOUNT_PENDING:
            return {
                'state_string': 'Waiting for bank approval',
                'buttons': [{
                    'label': 'Remove listing',
                    'function_key': 'RemoveListing',
                }]
            }
        elif booking_service.filter_reserved(car.booking_set.all()):
            return {
                'state_string': 'Waiting for insurance approval',
                'buttons': [{
                    'label': '',#'The driver is approved',
                    'function_key': '',#'ApproveInsurance',
                }]
            }
        elif booking_service.filter_accepted(car.booking_set.all()):
            return {
                'state_string': 'Ready to be picked up',
                'buttons': [{
                    'label': '',#'Contact the driver',
                    'function_key': '',#'ContactDriver',
                }]
            }
        elif booking_service.filter_active(car.booking_set.all()):
            b = booking_service.filter_active(car.booking_set.all()).first()
            return {
                'state_string': 'Rented until'.format(b.end_date.strftime('%b %d')),
                'buttons': [{
                    'label': '',#'Contact the driver',
                    'function_key': '',#'ContactDriver',
                }]
            }
        elif car_helpers.is_stale(car):
            return {
                'state_string': 'Listing expired',
                'buttons': [{
                    'label': 'Extend listing',
                    'function_key': 'ExtendListing',
                }]
            }
        else:
            return {
                'state_string': 'Listed',
                'buttons': [{
                    'label': 'Remove listing',
                    'function_key': 'RemoveListing',
                }]
            }

    def get_min_lease_display(self, obj):
        days = obj.minimum_rental_days()
        if not days:
            return "No minimum set"
        return '{} day'.format(days) + ('s' if days-1 else '')


class CarSerializer(CarCreateSerializer):
    class Meta(CarCreateSerializer.Meta):
        read_only_fields = CarCreateSerializer.Meta.read_only_fields + ('plate',)
