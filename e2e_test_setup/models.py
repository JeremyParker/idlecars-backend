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

        for i in xrange(3):
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
        server.factories.Booking.create(car=self.delorean, driver=self.driver)

    def _setup_drivers(self):
        '''
            Create 1 driver
        '''
        driver_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-7b33baf8-4aee-4e75-b7e1-0f591017251c-image.jpg"
        fhv_license_image = "https://s3.amazonaws.com/files.parsetfss.com/a0ed4ee2-63f3-4e88-a6ed-2be9921e9ed7/tfss-8e275adb-3202-444c-be99-7f9eac5dcdb0-image.jpg"

        self.user = server.factories.AuthUser.create(username='1234567891', email='user@test.com', first_name='Tom', last_name='Cat')
        self.driver = server.factories.Driver.create(auth_user=self.user, driver_license_image=driver_license_image, fhv_license_image=fhv_license_image)
