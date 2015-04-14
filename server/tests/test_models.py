# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from server import models
from idlecars import model_helpers

class TestUserAccount(TestCase):
    def test_full_name(self):
        person = models.UserAccount(
            first_name='Henry',
            last_name='Ford',
        )
        self.assertEqual(person.full_name(), "Henry Ford")

    def test_stripped_char_field(self):
        field = model_helpers.StrippedCharField()
        self.assertIsNone(field.get_prep_value(None))
        self.assertEqual('Charlie', field.get_prep_value('Charlie  '))
        self.assertEqual('ABCDEF', field.get_prep_value('ABCDEF'))

    def test_email_not_empty_string(self):
        user = models.UserAccount(email='')
        self.assertIsNone(user.email)


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
            person = models.UserAccount(
                first_name='First{}'.format(n),
                last_name='Last{}'.format(n),
                owner = owner,
            )
            person.save()

    def test_number(self):
        expected_results = [
            '',                     # empty string when there are no users
            '123-456-7890',         # the phone number of a single user
            'multiple values',      # string when > 1 user
            'multiple values',      # same string when > 1 user
        ]
        owner = models.Owner()
        owner.save()
        for n in range(3):
            self.assertEqual(owner.number(), expected_results[n])
            # create a person for next iteration
            person = models.UserAccount(
                phone_number='123-456-7890',
                owner = owner,
            )
            person.save()

    def test_email(self):
        expected_results = [
            '',                     # empty string when there are no users
            '0@email.com',          # the email of a single user
            'multiple values',      # string when > 1 user
            'multiple values',      # same string when > 1 user
        ]
        owner = models.Owner()
        owner.save()
        for n in range(3):
            self.assertEqual(owner.email(), expected_results[n])
            # add a person for next iteration
            person = models.UserAccount(
                email='{}@email.com'.format(n),
                owner = owner,
            )
            person.save()
