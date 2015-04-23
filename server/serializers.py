# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime

from rest_framework import serializers

from models import Car, UserAccount, Booking


class CarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    listing_features = serializers.SerializerMethodField()
    headline_features = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    cost_time = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = (
            'id',
            'name',
            'listing_features',
            'headline_features',
            'certifications',
            'details',
            'cost',
            'cost_time',
        )

    def get_name(self, obj):
        return unicode(obj.make_model)

    def get_listing_features(self, obj):
        return '{} minimum lease ∙ Available {} ∙ {}, {}'.format(
            Car.MIN_LEASE_CHOICES[obj.min_lease],
            self._available_string(obj),
            obj.owner.city,
            obj.owner.state_code,
        )

    def get_headline_features(self, obj):
        return [
            'Available {}'.format(self._available_string(obj)),
            '{} minimum'.format(Car.MIN_LEASE_CHOICES[obj.min_lease]),
            '{} deposit'.format(obj.solo_deposit),
        ]

    def get_certifications(self, obj):
        certs = [
            'Insurance is included',
            'Maintainance is included',
        ]
        if obj.base:
            certs = ['Base registration has been confirmed by idlecars'] + certs
        if obj.plate:
            certs = certs + ['Vehicle has TLC plates']
        return certs


    def get_details(self, obj):
        return [
            ['Hybrid', '☑' if obj.hybrid else '☐'],  # checkbox with or without check
            ['Location', ', '.join(l for l in [obj.owner.city, obj.owner.state_code] if l)],
            ['TLC Base', obj.base or 'Pending verification'],
        ]

    def get_cost(self, obj):
        return unicode(obj.solo_cost)

    def get_cost_time(self, obj):
        return 'a week'

    def _available_string(self, obj):
        if obj.next_available_date and obj.next_available_date > datetime.date.today():
            return '{d.month}/{d.day}'.format(d = obj.next_available_date)
        return "Now"


class UserAccountSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = UserAccount

    def create(self, validated_data):
        return UserAccount.objects.create(**validated_data)
 

class BookingSerializer(serializers.ModelSerializer):
    car_id = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    user_account = UserAccountSerializer(read_only=False)

    class Meta:
        model = Booking
        fields = ('user_account', 'car_id')

    def is_valid(self, raise_exception=False):
        # TODO - check that the car is available to be booked
        super(BookingSerializer, self).is_valid(raise_exception=True)

    def create(self, validated_data):
        user_account_data = validated_data.pop('user_account')
        user_account = UserAccount.objects.create(**user_account_data)
        car = validated_data['car_id']
        booking = Booking.objects.create(
            user_account = user_account,
            car = car,
        )
        return booking
