# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import connection
from django.conf import settings
from django.contrib import auth

from server import models
import server.factories

import owner_crm.factories

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

    def _setup_cars(self):
        '''
            Create 4 cars (also creates 4 owners)
        '''
        dmc = server.factories.MakeModel.create(make='DMC', model='Delorean')
        self.delorean = server.factories.BookableCar.create(make_model=dmc, year=1985)

        luxy = server.factories.MakeModel.create(make='Venus', model='Xtravaganza', lux_level=1)
        server.factories.BookableCar.create(make_model=luxy)

        for i in xrange(2):
            server.factories.BookableCar.create()

    def _setup_renewals(self):
        '''
            Create a renewal
        '''
        owner_crm.factories.Renewal.create(car=self.delorean, token='faketoken')

    def _setup_booking(self):
        '''
            Create a booking
        '''
        server.factories.Booking.create(car=self.delorean, driver=self.driver_incomplete)

    def _setup_user(self):
        '''
            Create 2 users(1 staff user)
        '''
        self.user_incomplete = server.factories.AuthUser.create(username='1234567891', email='tom@test.com', first_name='Tom', last_name='Cat')
        server.factories.StaffUser.create(username='idlecars')

    def _setup_drivers(self):
        '''
            Create 1 drivers
        '''
        driver_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-7b33baf8-4aee-4e75-b7e1-0f591017251c-image.jpg"
        fhv_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-8e275adb-3202-444c-be99-7f9eac5dcdb0-image.jpg"
        defensive_cert_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-e7cb3e75-f140-48ae-a16b-4550e249e62d-1439735074143-478457530.jpg"

        self.driver_incomplete = server.factories.Driver.create(auth_user=self.user_incomplete, driver_license_image=driver_license_image, fhv_license_image=fhv_license_image, defensive_cert_image=defensive_cert_image)
