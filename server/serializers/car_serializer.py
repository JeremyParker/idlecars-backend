# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ChoiceField

from idlecars import client_side_routes, fields
from server.models import Car, Owner
from server.fields import CarColorField
from server.services import car_helpers, booking as booking_service


class CarCreateSerializer(ModelSerializer):
    name = SerializerMethodField()
    state_string = SerializerMethodField()
    state_cta_string = SerializerMethodField()
    state_cta_key = SerializerMethodField()
    insurance = SerializerMethodField()
    listing_link = SerializerMethodField()
    available_date_display = SerializerMethodField()

    next_available_date = fields.DateArrayField(required=False, allow_null=True,)
    interior_color = CarColorField(required=False, allow_null=True,)
    exterior_color = CarColorField(required=False, allow_null=True,)
    status = ChoiceField(
        choices=Car.STATUS.keys(),
        required=False,
        allow_null=True,
    )

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
            'state_cta_string',
            'state_cta_key',
            'insurance',
            'listing_link',

            'solo_cost',
            'solo_deposit',
            'status',
            'next_available_date',
            'available_date_display',
            'min_lease',
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
            'state_cta_string',
            'state_cta_key',
            # fields we get from the TLC
            'make_model',
            'year',
            'base',
            'insurance',
       )

    def get_name(self, obj):
        return '{} {}'.format(obj.year, obj.make_model)

    def get_state_string(self, obj):
        return self._get_state_values(obj)['state_string']

    def get_state_cta_string(self, obj):
        return self._get_state_values(obj)['cta_string']

    def get_state_cta_key(self, obj):
        return self._get_state_values(obj)['cta_key']

    def get_insurance(self, obj):
        if obj.insurance:
            return obj.insurance.insurer_name
        return None

    def get_listing_link(self, obj):
        return client_side_routes.car_details_url(obj)

    def get_available_date_display(self, obj):
        if obj.status == 'busy':
            if not obj.next_available_date:
                return 'Unavailable'
            elif obj.next_available_date > timezone.now().date():
                return obj.next_available_date.strftime('%b %d')
        return 'Immediately'

    def _get_state_values(self, car):
        if not car_helpers.is_data_complete(car):
            return {
                'state_string': 'Waiting for information',
                'cta_string': 'Complete this listing',
                'cta_key': 'GoRequiredField',
            }
        elif car.status == Car.STATUS_BUSY:
            if car.next_available_date:
                return {
                    'state_string': 'Busy until {}'.format(car.next_available_date.strftime('%b %d')),
                    'cta_string': 'Change available date',
                    'cta_key': 'GoNextAvailableDate',
                }
            else:
                return {
                    'state_string': 'Not listed',
                    'cta_string': 'Relist',
                    'cta_key': 'GoNextAvailableDate',
                }
        elif car.owner and not car.owner.merchant_account_state or \
            car.owner.merchant_account_state == Owner.BANK_ACCOUNT_DECLINED:
            return {
                'state_string': 'Waiting for direct deposit information',
                'cta_string': 'Add bank details',
                'cta_key': 'AddBankLink',
            }
        elif car.owner and car.owner.merchant_account_state == Owner.BANK_ACCOUNT_PENDING:
            return {
                'state_string': 'Waiting for bank approval',
                'cta_string': 'Remove listing',
                'cta_key': 'RemoveListing',
            }
        elif booking_service.filter_reserved(car.booking_set.all()):
            return {
                'state_string': 'Waiting for insurance approval',
                'cta_string': '',#'The driver is approved',
                'cta_key': '',#'ApproveInsurance',
            }
        elif booking_service.filter_accepted(car.booking_set.all()):
            return {
                'state_string': 'Ready to be picked up',
                'cta_string': '',#'Contact the driver',
                'cta_key': '',#'ContactDriver',
            }
        elif booking_service.filter_active(car.booking_set.all()):
            b = booking_service.filter_active(car.booking_set.all()).first()
            return {
                'state_string': 'Rented until'.format(b.end_date.strftime('%b %d')),
                'cta_string': '',#'Contact the driver',
                'cta_key': '',#'ContactDriver',
            }
        elif car_helpers.is_stale(car):
            return {
                'state_string': 'Listing expired',
                'cta_string': 'Extend listing',
                'cta_key': 'ExtendListing',
            }
        else:
            return {
                'state_string': 'Listed',
                'cta_string': 'Remove listing',
                'cta_key': 'RemoveListing',
            }


class CarSerializer(CarCreateSerializer):
    class Meta(CarCreateSerializer.Meta):
        read_only_fields = CarCreateSerializer.Meta.read_only_fields + ('plate',)
