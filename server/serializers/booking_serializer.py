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
            if Booking.objects.filter(driver=driver, state__in=range(Booking.FLAKE + 1)):
                self._errors.update({
                    '_app_notifications': ['You have a conflicting rental.'],
                })

        # TODO(JP): double-check the car is available

        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    def create(self, validated_data):
        car = validated_data['car']
        driver = validated_data['driver']
        return booking_service.create_booking(car, driver)


booking_state_details = {
    Booking.PENDING: {"status": "Waiting for documents", "content": "You must upload your documents to rent this car.", "color": "rgb(255,51,51)"},
    Booking.COMPLETE: {"status": "Documents uploaded", "content": "Your documents are being reviewed.", "color": "rgb(255,128,0)"},
    Booking.REQUESTED: {"status": "Insurance processing", "content": "You are being added to this car's insurance.", "color": "rgb(255,128,0)"},
    Booking.ACCEPTED: {"status": "Ready for pickup", "content": "Please call us if you need assistance. 1-844-435-3227", "color": "rgb(255,51,51)"},
    Booking.BOOKED: {"status": "In progress", "content": "Happy driving!", "color": "rgb(0,204,0)"},
    Booking.FLAKE: {"status": "Waiting for documents", "content": "Please upload your driver documents.", "color": "rgb(255,51,51)"},
    Booking.TOO_SLOW: {"status": "Booked by another driver", "content": "Sorry, someone else booked this car.", "color": "rgb(0,0,0)"},
    Booking.OWNER_REJECTED: {"status": "Rejected by insurance", "content": "Sorry, you couldn't be added to the insurance.", "color": "rgb(0,0,0)"},
    Booking.DRIVER_REJECTED: {"status": "Canceled", "content": "Canceled by the driver.", "color": "rgb(0,0,0)"},
    Booking.MISSED: {"status": "Booked by another driver", "content": "Sorry, someone else booked this car.", "color": "rgb(0,0,0)"},
    Booking.TEST_BOOKING: {"status": "Test", "content": "This was marked as a test.", "color": "rgb(0,0,0)"},
    Booking.CANCELED: {"status": "Canceled", "content": "Canceled by the driver.", "color": "rgb(0,0,0)"},
}


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
            'state_details',
        )

    def update(self, instance, validated_data):
        '''
        Right now we only allow the API to update a booking's status to CANCELED. The booking
        must be in a state that can be canceled.
        '''
        if instance.state not in booking_service.cancelable_states:
            raise ValidationError('This rental can\'t be canceled at this time.')

        if 'state' not in validated_data or validated_data['state'] != Booking.CANCELED:
            raise ValidationError('This is not a valid state for a rental.')

        return booking_service.cancel_booking(instance)

    def get_state_details (self, obj):
        deets = booking_state_details[obj.state]
        deets.update({"cancelable": obj.state in booking_service.cancelable_states})
        return deets
