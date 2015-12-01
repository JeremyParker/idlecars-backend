# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, SerializerMethodField, ChoiceField

from idlecars import app_routes_driver, fields
from server.models import Car
from server.fields import CarColorField


class CarCreateSerializer(ModelSerializer):
    name = SerializerMethodField()
    state = SerializerMethodField()
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
            'state',
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

    def get_state(self, obj):
        # TODO - we need to figure out what the state of the car is in some efficient way
        return 'todo'

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


class CarSerializer(CarCreateSerializer):
    class Meta(CarCreateSerializer.Meta):
        read_only_fields = CarCreateSerializer.Meta.read_only_fields + ('plate',)
