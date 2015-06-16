# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """a user can edit only their own stuff"""
    def has_object_permission(self, request, view, obj):
        return request.user == obj.auth_user


class ReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD')