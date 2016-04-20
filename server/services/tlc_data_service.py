# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import datetime
from sodapy import Socrata
import dateutil.parser
import pytz

from django.conf import settings
from django.utils import timezone

from idlecars.fields import parse_phone_number
from server.models import Car, MakeModel
from server.tests.test_services.fake_tlc_data import TestClient


TLC_DOMAIN = 'data.cityofnewyork.us'
MEDALLION_VEHICLE_RESOURCE = 'rhe8-mgbb'


tlc_fields = [
    'found_in_tlc',
    'last_updated',
    'active_in_tlc',
    'year',
    'base',
    'base_number',
    'base_address',
    'base_telephone_number',
    'registrant_name',
    'vehicle_vin_number',
]

# FIELDS RETURNED BY SOCRATA API
# 'agent_address': '54-11 QUEENS BOULEVARD WOODSIDE NY 11377',
# 'agent_name': 'TAXIFLEET MANAGEMENT LLC',
# 'agent_number': '307',
# 'agent_telephone_number': '(718)779-5000',
# 'current_status': 'CUR',
# 'dmv_license_plate_number': '3A15A',
# 'last_updated_date': '2015-02-27T00:00:00',
# 'last_updated_time': '13:20',
# 'license_number': '3A15',
# 'medallion_type': 'NAMED DRIVER',
# 'model_year': '2012',
# 'name': 'THERMILDOR, JELON',
# 'type': 'MEDALLION',
# 'vehicle_type': 'HYB',
# 'vehicle_vin_number': '4T1BD1FK3CU050119'


def _copy_medallion_fields(car, tlc_data):
    car.found_in_tlc = True
    car.active_in_tlc = True
    car.last_updated = _localtime(tlc_data.get('last_updated_date', ''))
    car.year = int(tlc_data.get('model_year', ''))
    car.base = tlc_data.get('agent_name', '')
    car.base_number = tlc_data.get('agent_number', '')
    car.base_address = tlc_data.get('agent_address', '')
    car.base_telephone_number = parse_phone_number(tlc_data.get('agent_telephone_number', ''))
    car.registrant_name = tlc_data.get('name', '')
    car.vehicle_vin_number = tlc_data.get('vehicle_vin_number', '')
    car.medallion = True


def _localtime(datetime_str):
    return dateutil.parser.parse(datetime_str).replace(tzinfo=pytz.UTC)


def _get_resource(url):
    client = eval(settings.TLC_DATA_IMPLEMENTATION)(
        TLC_DOMAIN,
        settings.SOCRATA_APP_TOKEN,
        username=settings.SOCRATA_USERNAME,
        password=settings.SOCRATA_PASSWORD,
    )
    response_list = client.get('/resource/' + url)
    client.close()
    return response_list


def lookup_car_data(car):
    url = MEDALLION_VEHICLE_RESOURCE + '?license_number=' + car.plate + '&$limit=1'
    response_list = _get_resource(url)
    if not response_list:
        raise Car.DoesNotExist
    _copy_medallion_fields(car, response_list[0])


def _get_real_medallion():
    ''' For testing, we can retrieve the first car out of the database to use its plate
    for the requests that follow. This ensures that we get a "found" result. '''
    url = MEDALLION_VEHICLE_RESOURCE + '?$limit=1'
    response_list = _get_resource(url)
    return response_list[0]['license_number']

