# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions


class OwnsAddition(permissions.BasePermission):
    """a user can edit or get only their own addition"""
    def has_object_permission(self, request, view, obj):
        return request.user in obj.owner.auth_users.all()
