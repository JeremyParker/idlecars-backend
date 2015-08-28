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

class OwnsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.auth_user
