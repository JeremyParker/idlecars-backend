# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from idlecars import fields
from server.models import Car, Booking, Driver, booking_state
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


class BookingDetailsSerializer(serializers.ModelSerializer):
    car = car_serializer.CarSerializer()
    state_details = serializers.SerializerMethodField()
    start_time_display = serializers.SerializerMethodField()
    first_valid_end_time = serializers.SerializerMethodField()
    end_time = fields.DateArrayField()
    step = serializers.SerializerMethodField()
    step_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'id',
            'car',
            'state',
            'state_details',
            'step',
            'step_details',
            'end_time',
            'start_time_display',
            'first_valid_end_time',
        )
        read_only_fields = (
            'id',
            'car',
            'state_details',
            'step',
            'step_details',
            'start_time_display',
            'first_valid_end_time',
        )

    def update(self, instance, validated_data):
        '''
        Right now we only allow the API to update a booking's status to CANCELED. The booking
        must be in a state that can be canceled.
        '''
        if 'state' in validated_data:
            if validated_data['state'] == Booking.CANCELED:
                if instance.state not in booking_service.cancelable_states():
                    raise ValidationError('This rental can\'t be canceled at this time.')
                return booking_service.cancel_booking(instance)

            raise ValidationError('This is not a valid state for a rental.')

        if 'end_time' in validated_data:
            return booking_service.set_end_time(instance, validated_data['end_time'])

        return instance

    def get_state_details (self, obj):
        if not booking_state.states[obj.state]['visible']:
            return None
        deets = booking_state.states[obj.state]['details']
        deets.update({"cancelable": obj.state in booking_service.cancelable_states()})
        return deets
    def get_step(self, obj):
        return None

    def get_step_details(self, obj):
        if not booking_state.states[obj.state]['visible']:
            return None
        return None

    def get_start_time_display(self, obj):
        return booking_service.start_time_display(obj)

    def get_first_valid_end_time(self, obj):
        first_end = booking_service.first_valid_end_time(obj)
        return fields.format_date_array(first_end)
