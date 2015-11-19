# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from server.models import Car, CarCompatibility
from server.services import car as car_service, car_search
import owner_serializer


class ListingSerializer(ModelSerializer):
    name = SerializerMethodField()
    listing_features = SerializerMethodField()
    booked_features = SerializerMethodField()
    headline_features = SerializerMethodField()
    certifications = SerializerMethodField()
    details = SerializerMethodField()
    deposit = SerializerMethodField()
    cost_str = SerializerMethodField()
    cost_time = SerializerMethodField()
    cost_bucket = SerializerMethodField()
    image_url = SerializerMethodField()
    zipcode = SerializerMethodField()
    searchable = SerializerMethodField()
    compatibility = SerializerMethodField()

    class Meta:
        model = Car
        fields = (
            'id',
            'name',
            'listing_features',
            'booked_features',
            'headline_features',
            'certifications',
            'details',
            'deposit',
            'cost_str',
            'cost_time',
            'cost_bucket',
            'image_url',
            'zipcode',
            'searchable',
            'compatibility',
        )
        read_only_fields = (
            'id',
            'name',
            'listing_features',
            'booked_features',
            'headline_features',
            'certifications',
            'details',
            'cost_str',
            'cost_time',
            'cost_bucket',
            'image_url',
            'zipcode',
            'searchable',
            'compatibility',
        )

    def get_name(self, obj):
        return '{} {}'.format(obj.year, obj.make_model)

    def get_listing_features(self, obj):
        return '{} minimum ∙ Available {} ∙ {}, {}'.format(
            Car.MIN_LEASE_CHOICES[obj.min_lease],
            self._available_string(obj),
            obj.owner.city,
            obj.owner.state_code,
        )

    def get_booked_features(self, obj):
        return '{} minimum rental ∙ {}, {}'.format(
            Car.MIN_LEASE_CHOICES[obj.min_lease],
            obj.owner.city,
            obj.owner.state_code,
        )

    def get_headline_features(self, obj):
        return [
            'Available {}'.format(self._available_string(obj)),
            '{} minimum rental'.format(Car.MIN_LEASE_CHOICES[obj.min_lease]),
            '${} deposit'.format(obj.solo_deposit),
        ]

    def get_certifications(self, obj):
        return [
            'Base registration verified',
            'Vehicle has TLC plates',
            'Insurance is included',
            'Maintainance is included',
        ]

    def get_details(self, obj):
        details = [
            ['Location', ', '.join(l for l in [obj.owner.city, obj.owner.state_code] if l)],
            ['TLC Base', obj.base or 'Pending verification'],
        ]
        if obj.interior_color is not None:
            details = [['Interior color', Car.COLOR_CHOICES[obj.interior_color][1]],] + details
        if obj.exterior_color is not None:
            details = [['Exterior color', Car.COLOR_CHOICES[obj.exterior_color][1]],] + details
        if obj.display_mileage():
            details = [['Mileage', obj.display_mileage()],] + details
        if obj.hybrid:
            details = [['Hybrid ☑', ''],] + details
        return details

    def get_deposit(self, obj):
        return '${}'.format(obj.solo_deposit)

    def get_cost_str(self, obj):
        return str(obj.quantized_cost()).split('.')

    def get_cost_bucket(self, obj):
        # TODO: remove method when front end no longer needs it
        return car_search.get_cost_bucket(obj)

    def get_cost_time(self, obj):
        return 'a day'

    def get_image_url(self, obj):
        return car_service.get_image_url(obj)

    def get_zipcode(self, obj):
        if not obj.owner:
            return None
        return obj.owner.zipcode

    def get_searchable(self, obj):
        return car_search.search_attrs(obj)

    def get_compatibility(self, obj):
        return CarCompatibility(obj).all()

    def _available_string(self, obj):
        if obj.next_available_date and obj.next_available_date > timezone.now().date():
            return '{d.month}/{d.day}'.format(d = obj.next_available_date)
        return "Now"


class ListingPickupSerializer(ListingSerializer):
    owner = owner_serializer.OwnerContactSerializer()

    class Meta(ListingSerializer.Meta):
        fields = ListingSerializer.Meta.fields + (
            'owner',
            'plate',
        )
        read_only_fields = ListingSerializer.Meta.read_only_fields + (
            'owner',
            'plate',
        )
