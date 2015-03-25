# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import Client, TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from server.models import Driver
from server import factories

class AdminTest(TestCase):

    def setUp(self):
        # Reinitialize the client to turn off CSRF
        self.client = Client()

        username = 'test_user'
        pwd = 'secret'

        self.u = User.objects.create_user(username, '', pwd)
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.save()

        self.assertTrue(self.client.login(username=username, password=pwd),
            "Logging in user %s, pwd %s failed." % (username, pwd))

    def tearDown(self):
        self.client.logout()
        self.u.delete()

    def test_all_admin_pages(self):
        ''' 
        Check all the automatically generated admin pages that Django provides for 
        all the models in our app.
        '''
        for model in [
            # (slug, factory) pairs for all the admin-accessible models in the app:
            ('fleetpartner', factories.FleetPartner),
            ('driver', factories.Driver),
        ]:
            # get the views that don't need an existing object
            for view in [
                'admin:server_{}_add',
                'admin:server_{}_changelist',
            ]:
                url = reverse(view.format(model[0]))
                response = self.client.get(url)
                self.assertEquals(200, response.status_code)

            # get all the views for an individual object
            obj = model[1].create()
            for view in [
                'admin:server_{}_history',
                'admin:server_{}_change',
                'admin:server_{}_delete',
            ]:
                url = reverse(view.format(model[0]), args=(obj.pk,))
                response = self.client.get(url)
                self.assertEquals(200, response.status_code)


    def test_driver_admin(self):
        self.assertEquals(Driver.objects.count(), 0)

        post_data = {
            'first_name': 'Henry',
            'last_name': 'Ford',
            'phone_number': '555-555-1212',
            'email': 'example@wherever.com',
        }

        response = self.client.post(reverse('admin:server_driver_add'), post_data)

        self.assertRedirects(response, reverse('admin:server_driver_changelist'))
        self.assertEquals(Driver.objects.count(), 1)
