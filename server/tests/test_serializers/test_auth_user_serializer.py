# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.contrib.auth import models as auth_models

from server import serializers, factories

class TestAuthUser(TestCase):
    def test_serialize(self):
        auth_user = factories.AuthUser.create()
        auth_user.set_password('test')

        data = serializers.AuthUserSerializer(auth_user).data
        self.assertEqual(auth_user.username, data['phone_number'])
        self.assertFalse('password' in data)

        # unchanged fields
        self.assertEqual(auth_user.first_name, data['first_name'])
        self.assertEqual(auth_user.last_name, data['last_name'])
        self.assertEqual(auth_user.email, data['email'])
        self.assertEqual(auth_user.id, data['id'])

    def test_create(self):
        data = {
            'phone_number': '+46(7)2274669320',
            'password': 'test',
        }
        serializer = serializers.AuthUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

        new_auth_user = serializer.save()
        self.assertEqual(new_auth_user.username, data['phone_number'])
        self.assertNotEqual(new_auth_user.password, data['password'])

    def test_update(self):
        instance = auth_models.User.objects.create_user(
            username='test user',
            password='test pass',
            email='dude@whatever.com',
            first_name='danny',
            last_name='goldman',
        )
        data = {
            'password': 'test_different',
            'first_name': 'abdul',
        }
        serializer = serializers.AuthUserSerializer(instance=instance, data=data, partial=True)
        serializer.is_valid()
        self.assertEqual(serializer.errors, {})
        serializer.save()

        updated_instance = auth_models.User.objects.get(pk=instance.pk)
        self.assertEqual(updated_instance.first_name, data['first_name'])
        self.assertNotEqual(instance.password, data['password'])

