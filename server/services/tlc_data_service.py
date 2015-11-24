# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from sodapy import Socrata
import dateutil.parser
import pytz

from django.conf import settings
from django.utils import timezone

from idlecars.fields import parse_phone_number
from server.models import Car, MakeModel, Insurance
from server.tests.test_services.fake_tlc_data import TestClient


TLC_DOMAIN = 'data.cityofnewyork.us'


# dict of fields that this module will look up and copy into the given Car object
fhv_fields = [
    'found_in_tlc',
    'last_updated',
    'active_in_tlc',
    'year',
    'base',
    'base_number',
    'base_address',
    'base_telephone_number',
    'base_type',
    'registrant_name',
    'expiration_date',
    'vehicle_vin_number',

    'insurance'
    'make_model',
]


def _localtime(datetime_str):
    return timezone.localtime(dateutil.parser.parse(datetime_str).replace(tzinfo=pytz.UTC))


def lookup_fhv_data(car):
    '''
    Looks up the given car in the TLC database, and fills in details. If the car's plate
    doesn't exist in the db, we raise a Car.DoesNotExist.
    '''
    client = eval(settings.TLC_DATA_IMPLEMENTATION)(
        TLC_DOMAIN,
        settings.SOCRATA_APP_TOKEN,
        username=settings.SOCRATA_USERNAME,
        password=settings.SOCRATA_PASSWORD,
    )
    url = '/resource/' + settings.FHV_VEHICLE_RESOURCE + '?dmv_license_plate_number='
    response_list = client.get(url + car.plate)
    client.close()

    if not response_list:
        raise Car.DoesNotExist

    tlc_data = response_list[0]
    car.found_in_tlc = True
    car.last_updated = _localtime(tlc_data['last_time_updated'])
    car.active_in_tlc = True if tlc_data['active'] == 'YES' else False
    car.year = int(tlc_data['vehicle_year'])
    car.base = tlc_data['base_name']
    car.base_number = tlc_data['base_number']
    car.base_address = tlc_data['base_address']
    car.base_telephone_number = parse_phone_number(tlc_data['base_telephone_number'])
    car.base_type = Car.BASE_TYPE_LIVERY if tlc_data['base_type'] == 'LIVERY' else Car.BASE_TYPE_PARATRANS
    car.registrant_name = tlc_data['name']
    car.expiration_date = _localtime(tlc_data['expiration_date'])
    car.vehicle_vin_number = tlc_data['vehicle_vin_number']

    # TODO: look up the car in the db and get more details
    car.make_model = MakeModel.objects.last()
