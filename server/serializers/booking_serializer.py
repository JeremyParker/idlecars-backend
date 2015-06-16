# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from server.models import Car, Booking, Driver
from server.services import booking as booking_service
from server.serializers import UserAccountSerializer


class BookingSerializer(serializers.ModelSerializer):
    car_id = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    driver_id = serializers.PrimaryKeyRelatedField(queryset=Driver.objects.all())  #TODO - all?
    user_account = UserAccountSerializer(read_only=False)

    class Meta:
        model = Booking
        fields = ('user_account', 'car_id')

    def is_valid(self, raise_exception=False):
        # TODO - check that the car is available to be booked
        super(BookingSerializer, self).is_valid(raise_exception=True)

    def create(self, validated_data):
        user_account_data = validated_data.pop('user_account')
        car = validated_data['car_id']
        return booking_service.create_booking(user_account_data, car)
        # TODO(JP) - error handling if car is already booked, or user is banned, ...etc
