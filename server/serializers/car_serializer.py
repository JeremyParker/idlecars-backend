# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework import serializers

from server.models import Car, CarCompatibility
from server.services import car as car_service
from server.services import rideshare_flavor_service
from server.serializers import RideshareFlavorSerializer


class CarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    listing_features = serializers.SerializerMethodField()
    booked_features = serializers.SerializerMethodField()
    headline_features = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    cost_time = serializers.SerializerMethodField()
    cost_bucket = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    zipcode = serializers.SerializerMethodField()
    compatibility = serializers.SerializerMethodField(read_only=True)

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
            'cost',
            'cost_time',
            'cost_bucket',
            'image_url',
            'zipcode',
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

    def get_cost(self, obj):
        return unicode(self._normalized_cost(obj))

    def get_cost_bucket(self, obj):
        norm = self._normalized_cost(obj)
        if norm < 60:
            return 'cheap'
        elif norm < 80:
            return 'medium'
        else:
            return 'pricey'

    def get_cost_time(self, obj):
        return 'a day'

    def get_image_url(self, obj):
        return car_service.get_image_url(obj)

    def get_zipcode(self, obj):
        if not obj.owner:
            return None
        return obj.owner.zipcode

    def get_compatibility(self, obj):
        compatible_flavors = rideshare_flavor_service.get_rideshare_flavors(obj)
        return RideshareFlavorSerializer(compatible_flavors, many=True).data

    def _normalized_cost(self, obj):
        return int((obj.solo_cost + 6) / 7)

    def _available_string(self, obj):
        if obj.next_available_date and obj.next_available_date > timezone.now().date():
            return '{d.month}/{d.day}'.format(d = obj.next_available_date)
        return "Now"
