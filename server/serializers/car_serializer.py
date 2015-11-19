# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from idlecars import client_side_routes

from server.models import Car


class CarSerializer(ModelSerializer):
    name = SerializerMethodField()
    state = SerializerMethodField()
    insurance = SerializerMethodField()
    listing_link = SerializerMethodField()

    class Meta:
        model = Car
        fields = (
            'created_time',
            'id',
            'name',
            'plate',
            'base',
            'state',
            'insurance',
            'listing_link',

            'solo_cost',
            'solo_deposit',
            'status',
            'next_available_date',
            'min_lease',
            'exterior_color',
            'interior_color',
            'last_known_mileage',
            # 'split_cost',
            # 'split_deposit',
        )
        read_only_fields = (
            'id',
            'name',
            'created_time',
            'plate',
            'base',
            'state',
            'insurance',
            'listing_link',
       )

    def get_name(self, obj):
        return '{} {}'.format(obj.year, obj.make_model)

    def get_state(self, obj):
        # TODO - we need to figure out what the state of the car is in some efficient way
        return 'todo'

    def get_insurance(self, obj):
        if obj.insurance:
            return obj.insurance.name
        return None

    def get_listing_link(self, obj):
        return client_side_routes.car_details_url(obj)
