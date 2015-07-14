# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from server.models import Car, Booking, Driver
from server.services import booking as booking_service
from server.serializers import car_serializer


class BookingSerializer(serializers.ModelSerializer):
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    driver = serializers.ReadOnlyField(source='driver.pk')

    class Meta:
        model = Booking
        fields = ('id', 'car', 'driver')
        read_only_fields = ('id', 'driver')

    def is_valid(self, raise_exception=False):
        valid = super(BookingSerializer, self).is_valid(raise_exception=raise_exception)
        if not valid:
            return valid

        # TODO(JP): make this booking-check aware of end-times, so we can book after booking ends.
        if self.context['request'].method == 'POST':
            driver = Driver.objects.get(auth_user=self.context['request'].user)
            # look for bookings up to but not including "BOOKED" state. I.e. bookings in progress.
            if Booking.objects.filter(driver=driver, state__in=range(Booking.FLAKE)):
                self._errors.update({
                    'detail': 'You already have a booking in progress.',
                    '_app_notifications': ['You already have a booking in progress.'],
                })

        # TODO(JP): double-check the car is available

        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)


    def create(self, validated_data):
        car = validated_data['car']
        driver = validated_data['driver']
        return booking_service.create_booking(car, driver)


class BookingDetailsSerializer(serializers.ModelSerializer):
    car = car_serializer.CarSerializer()

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'state',
        )
        read_only_fields = ('car', 'state')
