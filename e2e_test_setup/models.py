# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import connection
from django.conf import settings
from django.contrib import auth
from rest_framework.authtoken.models import Token

from server import models
import server.factories
from server.services import owner_service

from owner_crm.models import PasswordReset
import owner_crm.factories

from rest_framework.authtoken.models import Token


class E2ETestSetup():
    def __init__(self):
        if settings.WARNING__ENABLE_TEST_SETUP_ENDPOINT__TEST_MODE_ONLY:
            self.cursor = connection.cursor()
        else:
            raise Exception('YOU! SHALL! NOT! PASS!!!')

    def perform(self):
        self._truncate_tables()
        self._setup_cars()
        self._setup_renewals()
        self._setup_user()
        self._setup_drivers()
        self._setup_booking()
        self._setup_owner()
        self._reset_token()

    def _truncate_tables(self):
        tables = (
            models.Car._meta.db_table,
            models.Booking._meta.db_table,
            models.Owner._meta.db_table,
            models.MakeModel._meta.db_table,
            models.UserAccount._meta.db_table,
            models.Driver._meta.db_table,
            auth.models.User._meta.db_table,
        )
        table_list = ','.join(tables)
        self.cursor.execute('TRUNCATE TABLE {} RESTART IDENTITY CASCADE;'.format(table_list))

    def _reset_token(self):
        Token.objects.filter(user=self.user_insurance_approved).update(key='insurance_approved')
        Token.objects.filter(user=self.user_without_booking).update(key='without_booking')
        Token.objects.filter(user=self.user_without_docs).update(key='without_docs')
        Token.objects.filter(user=self.user_without_docs_approved).update(key='without_docs_approved')

        Token.objects.filter(user=self.owner_user).update(key='owner')
        PasswordReset.objects.filter(auth_user=self.owner_user).update(token='test')

    def _setup_cars(self):
        '''
            Create 4 cars (also creates 4 owners)
        '''
        dmc = server.factories.MakeModel.create(make='DMC', model='Delorean')
        self.delorean = server.factories.BookableCar.create(make_model=dmc, year=1985)

        luxy = server.factories.MakeModel.create(make='Venus', model='Xtravaganza', lux_level=1)
        server.factories.BookableCar.create(make_model=luxy)

        benz = server.factories.MakeModel.create(make='Benz', model='C350', lux_level=1)
        self.benz = server.factories.BookableCar.create(make_model=benz)

        for i in xrange(2):
            server.factories.BookableCar.create()

    def _setup_renewals(self):
        '''
            Create a renewal
        '''
        owner_crm.factories.Renewal.create(car=self.delorean, token='faketoken')

    def _setup_booking(self):
        '''
            Create 3 bookings
        '''
        server.factories.Booking.create(car=self.delorean, driver=self.driver_without_docs)
        server.factories.AcceptedBooking.create(car=self.benz, driver=self.driver_insurance_approved)
        server.factories.Booking.create(car=self.benz, driver=self.driver_without_docs_approved)

    def _setup_user(self):
        '''
            Create 6 users(1 staff user)
        '''
        self.user_owner = server.factories.AuthUser.create(
            username='9876543210',
            email='craig@test.com',
            first_name='Craig',
            last_name='List'
        )
        self.user_without_booking = server.factories.AuthUser.create(
            username='1234567891',
            email='jerry@test.com',
            first_name='Jerry',
            last_name='Mouse'
        )
        self.user_without_docs = server.factories.AuthUser.create(
            username='1234567892',
            email='tom@test.com',
            first_name='Tom',
            last_name='Cat'
        )
        self.user_without_docs_approved = server.factories.AuthUser.create(
            username='1234567893',
            email='donald@test.com',
            first_name='donald',
            last_name='Duck'
        )
        self.user_insurance_approved = server.factories.AuthUser.create(
            username='1234567894',
            email='kerry@test.com',
            first_name='Kerry',
            last_name='Goose')
        server.factories.StaffUser.create(username='idlecars') # just want to access admin, easier to check database

    def _setup_owner(self):
        '''
            Create an owner
        '''
        owner = server.factories.Owner.create()
        owner.auth_users.add(self.user_owner)
        self.owner_user = owner_service.invite_legacy_owner(self.user_owner.username)

    def _setup_drivers(self):
        '''
            Create 4 drivers
        '''
        driver_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-7b33baf8-4aee-4e75-b7e1-0f591017251c-image.jpg"
        fhv_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-8e275adb-3202-444c-be99-7f9eac5dcdb0-image.jpg"
        defensive_cert_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-e7cb3e75-f140-48ae-a16b-4550e249e62d-1439735074143-478457530.jpg"

        server.factories.Driver.create(
            auth_user=self.user_without_booking,
            driver_license_image=driver_license_image,
            fhv_license_image=fhv_license_image,
            defensive_cert_image=defensive_cert_image,
            address_proof_image=driver_license_image
        )
        self.driver_without_docs = server.factories.Driver.create(auth_user=self.user_without_docs)
        self.driver_without_docs_approved = server.factories.Driver.create(
            auth_user=self.user_without_docs_approved,
            driver_license_image=driver_license_image,
            fhv_license_image=fhv_license_image,
            defensive_cert_image=defensive_cert_image,
            address_proof_image=driver_license_image
        )
        self.driver_insurance_approved = server.factories.ApprovedDriver.create(
            auth_user=self.user_insurance_approved,
            driver_license_image=driver_license_image,
            fhv_license_image=fhv_license_image,
            defensive_cert_image=defensive_cert_image,
            address_proof_image=driver_license_image
        )
