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
    cost_bucket = serializers.SerializerMethodField()
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
            'cost_bucket',
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
        if obj.min_lease in ['_01_no_min', '_02_one_week']:
            return unicode(self._normalized_cost(obj))
        return unicode(obj.solo_cost)

    def get_cost_bucket(self, obj):
        norm = self._normalized_cost(obj)
        if norm < 50:
            return '$'
        elif norm < 80:
            return '$$'
        else:
            return '$$$'

    def get_cost_time(self, obj):
        if obj.min_lease in ['_01_no_min', '_02_one_week']:
            return 'a day'
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

    def _normalized_cost(self, obj):
        return int((obj.solo_cost + 6) / 7)
