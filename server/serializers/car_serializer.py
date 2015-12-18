# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.utils import timezone
from django.conf import settings
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ChoiceField
from rest_framework.exceptions import ValidationError

from idlecars import app_routes_driver, fields
from server.models import Car, Owner
from server.fields import CarColorField
from server.services import car_helpers, booking as booking_service, car as car_service


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

            'weekly_rent',
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

    def update(self, instance, validated_data):
        if 'owner' in validated_data and car_service.has_booking_in_progress(instance):
            raise ValidationError('This car has a booking in progress so it cannot be deleted.')
        return super(CarCreateSerializer, self).update(instance, validated_data)

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

    def get_min_lease_display(self, obj):
        days = obj.minimum_rental_days()
        if not days:
            return "No minimum set"
        return '{} day'.format(days) + ('s' if days-1 else '')

    def _get_state_values(self, car):
        if not car_helpers.is_data_complete(car):
            return {
                'state_string': 'Waiting for information',
                'buttons': [
                    # {
                    #     'label': 'Complete this listing',
                    #     'function_key': 'GoRequiredField',
                    # }
                ]
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
            if car.next_available_date:
                return {
                    'state_string': 'Waiting for bank account approval.',
                    'buttons': [{
                        'label': 'Remove listing',
                        'function_key': 'RemoveListing',
                    }]
                }
            else:
                return {
                    'state_string': 'Not listed.',
                    'buttons': [{
                        'label': 'List this car',
                        'function_key': 'Relist',
                    }]
                }
        elif booking_service.filter_requested(car.booking_set.all()):
            return {
                'state_string': 'Booked. Waiting for insurance approval.',
                'buttons': [
                    # {
                    #     'label': 'The driver is approved',
                    #     'function_key': 'ApproveInsurance',
                    # },
                    # {
                    #     'label': 'The driver was rejected from the insurance',
                    #     'function_key': 'RejectInsurance',
                    # },
                    {
                        'label': 'This car is no longer available',
                        'function_key': 'RemoveListing',
                    },
                ]
            }
        elif booking_service.filter_accepted(car.booking_set.all()):
            return {
                'state_string': 'Booked. The driver will contact you to arrange pickup.',
                'buttons': [
                # {
                    # TODO
                    # 'label': 'Contact the driver',
                    # 'function_key': 'ContactDriver',
                # }
                ]
            }
        elif booking_service.filter_active(car.booking_set.all()):
            b = booking_service.filter_active(car.booking_set.all()).first()
            return {
                'state_string': 'Rented until {}'.format(b.end_time.strftime('%b %d')),
                'buttons': [
                # {
                    # TODO
                    # 'label': 'Contact the driver',
                    # 'function_key': 'ContactDriver',
                # }
                ]
            }
        elif not car.next_available_date:
            return {
                'state_string': 'Not listed.',
                'buttons': [{
                    'label': 'List this car',
                    'function_key': 'Relist',
                }]
            }
        elif car_helpers.is_stale(car):
            return {
                'state_string': 'Listing expired.',
                'buttons': [
                    {
                        'label': 'Renew this listing',
                        'function_key': 'RenewListing',
                    },
                    {
                        'label': 'Remove listing',
                        'function_key': 'RemoveListing',
                    }
                ]
            }
        elif car.next_available_date > car_helpers.next_available_date_threshold:
            # NOTE: This should result in the same logic as car_helpers.filter_bookable()
                return {
                    'state_string': 'Not listed. Busy until {}.'.format(car.next_available_date.strftime('%b %d')),
                    'buttons': [
                        {
                            'label': 'List this car',
                            'function_key': 'Relist',
                        },
                        {
                            'label': 'Change availability',
                            'function_key': 'GoNextAvailableDate',
                        },
                    ]
                }
        else:
            listing_expiration_date = car.last_status_update + datetime.timedelta(
                days=settings.STALENESS_LIMIT
            )
            result = {
                'state_string': 'Listed. This listing expires {}'.format(
                    listing_expiration_date.strftime('%b %d')
                ),
                'buttons': [{
                    'label': 'Remove listing',
                    'function_key': 'RemoveListing',
                }]
            }
            # if the last update time was more than two hours ago, let them refresh it again
            if car.last_status_update < timezone.now() - datetime.timedelta(hours=2):
                result['buttons'].insert(0, {
                    'label': 'Extend this listing',
                    'function_key': 'RenewListing',
                })
            return result

class CarSerializer(CarCreateSerializer):
    class Meta(CarCreateSerializer.Meta):
        read_only_fields = CarCreateSerializer.Meta.read_only_fields + ('plate',)
