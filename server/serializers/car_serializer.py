# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone

from rest_framework import serializers

from server.models import Car
from server.services import car as car_service


class CarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    listing_features = serializers.SerializerMethodField()
    booked_features = serializers.SerializerMethodField()
    headline_features = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    cost_time = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    zipcode = serializers.SerializerMethodField()

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
            'image_url',
            'zipcode',
        )

    def get_name(self, obj):
        return '{} {}'.format(obj.year, obj.make_model)

    def get_listing_features(self, obj):
        return '{} minimum rental ∙ Available {} ∙ {}, {}'.format(
            Car.MIN_LEASE_CHOICES[obj.min_lease],
            self._available_string(obj),
            obj.owner.city,
            obj.owner.state_code,
        )

    def get_booked_features(self, obj):
        return '{} minimum ∙ {}, {}'.format(
            Car.MIN_LEASE_CHOICES[obj.min_lease],
            obj.owner.city,
            obj.owner.state_code,
        )

    def get_headline_features(self, obj):
        return [
            'Available {}'.format(self._available_string(obj)),
            '{} minimum'.format(Car.MIN_LEASE_CHOICES[obj.min_lease]),
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
        return unicode(obj.solo_cost)

    def get_cost_time(self, obj):
        return 'a week'

    def _available_string(self, obj):
        if obj.next_available_date and obj.next_available_date > timezone.now().date():
            return '{d.month}/{d.day}'.format(d = obj.next_available_date)
        return "Now"

    def get_image_url(self, obj):
        return car_service.get_image_url(obj)

    def get_zipcode(self, obj):
        if not obj.owner:
            return None
        return obj.owner.zipcode
