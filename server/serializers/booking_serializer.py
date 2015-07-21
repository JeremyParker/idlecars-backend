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
    state_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'state',
            'state_details',
        )
        read_only_fields = (
            'id',
            'car',
        )

    def update(self, instance, validated_data):
        new_state = validated_data['state']
        old_state = instance.state
        if new_state != old_state and new_state == Booking.CANCELED:
            return booking_service.cancel_booking(instance)
        return instance

    def get_state_details (self, obj):
        state_details = {
            1: {"status": "Awaiting document upload", "content": "Please upload your documents.", "color": "rgb(255,51,51)"},
            2: {"status": "Awaiting idlecars approval", "content": "We'll notify you once you are approved.", "color": "rgb(255,128,0)"},
            3: {"status": "Awaiting insurance approval", "content": "We'll notify you once you are approved.", "color": "rgb(255,128,0)"},
            4: {"status": "Awaiting pickup", "content": "Please call us if you need assistance. 1-844-435-3227", "color": "rgb(255,51,51)"},
            5: {"status": "Booked", "content": "Enjoy your ride.", "color": "rgb(0,204,0)"},
        }
        default_details = {"status": "Booking expired", "content": "Sorry, your booking has expired.", "color": "rgb(255,51,51)"}
        return state_details.get(obj.state, default_details)
