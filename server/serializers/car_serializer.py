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
    shift_display = SerializerMethodField()

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

            'shift',
            'shift_details',
            'shift_display',
            'weekly_rent',
            'deposit',
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
            'shift_display',
            'min_lease_display',
            # fields we get from the TLC
            'make_model',
            'year',
            'base',
            'insurance',
       )

    def update(self, instance, validated_data):
        if 'owner' in validated_data:
            if car_service.has_booking_in_progress(instance):
                raise ValidationError('A driver is associated with this shift. Remove the driver, then delete.')
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

    def get_shift_display(self, obj):
        return '{} {}'.format(
            Car.SHIFT_CHOICES[obj.shift][1],
            obj.shift_details
        )

    def _get_state_values(self, car):
        if not car_helpers.is_data_complete(car):
            return {
                'state_string': 'Waiting for information. Tap here.',
                'buttons': []
            }

        if not car.next_available_date:
            return {
                'state_string': 'Not listed.',
                'buttons': [{
                    'label': 'List this shift',
                    'function_key': 'Relist',
                }]
            }

        if booking_service.filter_requested(car.booking_set.all()):
            return {
                'state_string': 'Requested. Check your email for documentation.',
                'buttons': [
                    {
                        'label': 'Add this driver',
                        'function_key': 'ApproveInsurance',
                    },
                    {
                        'label': 'Don\'t add this driver',
                        'function_key': 'RejectInsurance',
                    },
                    {
                        'label': 'This shift is no longer available',
                        'function_key': 'RemoveListing',
                    },
                ]
            }

        active_bookings = booking_service.filter_returned(car.booking_set.all())
        if active_bookings:
            return {
                'state_string': 'Rented to {}'.format(active_bookings.first().driver.admin_display()),
                'buttons': [{
                    'label': 'Remove this driver',
                    'function_key': 'ReturnConfirm',
                }]
            }

        if car_helpers.is_stale(car):
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

        if car.next_available_date > car_helpers.next_available_date_threshold:
            # NOTE: This should result in the same logic as car_helpers.filter_bookable()
            return {
                'state_string': 'Not listed. Will be listed on {}.'.format(car.next_available_date.strftime('%b %d')),
                'buttons': [
                    {
                        'label': 'List this shift',
                        'function_key': 'Relist',
                    },
                    {
                        'label': 'Change availability',
                        'function_key': 'GoNextAvailableDate',
                    },
                ]
            }

        # If no other cases evaluated to true...
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
