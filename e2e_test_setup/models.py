# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.db import connection
from django.conf import settings

from server import models
import server.factories

import crm.factories

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

    def _truncate_tables(self):
        tables = (
            models.Car._meta.db_table,
            models.Booking._meta.db_table,
            models.Owner._meta.db_table,
            models.MakeModel._meta.db_table,
            models.UserAccount._meta.db_table,
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
        crm.factories.Renewal.create(car=self.delorean, token='faketoken')
