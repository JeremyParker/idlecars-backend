# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions


class OwnsDriver(permissions.BasePermission):
    """a user can edit or get only their own driver"""
    def has_object_permission(self, request, view, obj):
        return request.user == obj.auth_user


class OwnsBooking(permissions.BasePermission):
    """a user can edit or get only their own bookings"""
    def has_object_permission(self, request, view, obj):
        return request.user == obj.driver.auth_user


class IsBookingCarOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, booking):
        return request.user in booking.car.owner.auth_users.all()


class OwnsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user in obj.auth_users.all()


class OwnsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj


class OwnsCar(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return not obj.owner or request.user in obj.owner.auth_users.all()


class IsAuthenticatedOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return request.user.owner_set.exists()
