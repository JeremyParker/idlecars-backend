# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User

from server import models, factories
from idlecars import model_helpers


class TestOwner(TestCase):
    def test_name(self):
        expected_results = [
            '',                             # empty string when there are no users
            'First0 Last0',                 # the name of a single user
            'First0 Last0, First1 Last1',   # both names when > 1 user
        ]
        owner = models.Owner()
        owner.save()
        for n in range(2):
            self.assertEqual(owner.name(), expected_results[n])
            person = User(
                first_name='First{}'.format(n),
                last_name='Last{}'.format(n),
            )
            owner.auth_users.add(person)

    def test_number(self):
        expected_results = [
            '',                     # empty string when there are no users
            '123-456-7890',         # the phone number of a single user
            'multiple values',      # string when > 1 user
            'multiple values',      # same string when > 1 user
        ]
        owner = models.Owner.create()
        for n in range(3):
            self.assertEqual(owner.number(), expected_results[n])
            # create a person for next iteration
            person = User(phone_number='123-456-7890',)
            owner.auth_users.add(person)

    def test_email(self):
        expected_results = [
            '',                     # empty string when there are no users
            '0@email.com',          # the email of a single user
            'multiple values',      # string when > 1 user
            'multiple values',      # same string when > 1 user
        ]
        owner = models.Owner.create()
        for n in range(3):
            self.assertEqual(owner.email(), expected_results[n])
            # add a person for next iteration
            person = User(email='{}@email.com'.format(n),)
            owner.auth_users.add(person)


class TestDriver(TestCase):
    def test_admin_display(self):
        auth_user = factories.AuthUser(first_name='', last_name='')
        driver = factories.Driver(auth_user=auth_user)
        self.assertEqual(driver.auth_user.username, driver.admin_display())

    def test_changing_docs_unchecks_confirmation(self):
        driver = factories.ApprovedDriver.create()
        driver.driver_license_image = 'http://wondernuts.com/9d80dec789a7b.jpg'
        driver.save()
        self.assertFalse(driver.documentation_approved)


class TestCar(TestCase):
    def test_set_status_sets_date(self):
        # we have to have real dependent objects so save() will work
        owner = factories.Owner.create()
        make_model = factories.MakeModel.create()
        car = models.Car(
            owner = owner,
            make_model = make_model,
        )
        car.save()
        self.assertIsNotNone(car.last_status_update)

    def test_save_updates_mileage_date(self):
        car = factories.Car.create()
        car.last_known_mileage = 10345
        car.save()
        self.assertEqual(
            car.last_mileage_update.replace(microsecond=0),
            timezone.now().replace(microsecond=0),
        )

    def test_save_updates_status_date(self):
        car = factories.Car.create()
        car.status = models.Car.STATUS_AVAILABLE
        car.save()
        self.assertEqual(
            car.last_status_update.replace(microsecond=0),
            timezone.now().replace(microsecond=0),
        )
