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
FHV_VEHICLE_RESOURCE = '8wbx-tsch'
MEDALLION_VEHICLE_RESOURCE = 'rhe8-mgbb'
INSURANCE_RESOURCE = 'cw8b-zbc3'


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
]


def _copy_fhv_fields(car, tlc_data):
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


def _copy_medallion_fields(car, tlc_data):
    car.found_in_tlc = True
    car.last_updated = _localtime(tlc_data['last_updated_date'])
    car.active_in_tlc = True
    car.year = int(tlc_data['model_year'])
    car.base = tlc_data['agent_name']
    car.base_number = tlc_data['agent_number']
    car.base_address = tlc_data['agent_address']
    car.base_telephone_number = parse_phone_number(tlc_data['agent_telephone_number'])
    # car.base_type = Car.BASE_TYPE_LIVERY if tlc_data['base_type'] == 'LIVERY' else Car.BASE_TYPE_PARATRANS
    car.registrant_name = tlc_data['name']
    # car.expiration_date = _localtime(tlc_data['expiration_date'])
    car.vehicle_vin_number = tlc_data['vehicle_vin_number']
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


def _lookup_fhv_data(car):
    '''
    Looks up the given car in the TLC database, and fills in details. If the car's plate
    doesn't exist in the db, we raise a Car.DoesNotExist.
    '''
    url = FHV_VEHICLE_RESOURCE + '?dmv_license_plate_number=' + car.plate
    response_list = _get_resource(url)
    if not response_list:
        raise Car.DoesNotExist
    _copy_fhv_fields(car, response_list[0])


def _lookup_medallion_data(car):
    url = MEDALLION_VEHICLE_RESOURCE + '?dmv_license_plate_number=' + car.plate + '&$limit=1'
    response_list = _get_resource(url)
    if not response_list:
        raise Car.DoesNotExist
    _copy_medallion_fields(car, response_list[0])


def lookup_car_data(car):
    try:
        _lookup_fhv_data(car)
    except Car.DoesNotExist:
        _lookup_medallion_data(car)


def lookup_insurance_data(car):
    '''
    Looks up the insurance information based on the VIN of the car.
    '''
    url = INSURANCE_RESOURCE + '?$q=' + car.plate
    response_list = _get_resource(url)
    if not response_list:
        return

    insurance_code = response_list[0]['automobile_insurance_code']
    try:
        car.insurance = Insurance.objects.get(insurance_code=insurance_code)
    except Insurance.DoesNotExist:
        car.insurance = Insurance.objects.create(
            insurance_code=insurance_code,
            insurer_name='Unknown Insurer with TLC ID {}'.format(insurance_code)
        )
    car.insurance_policy_number = response_list[0]['automobile_insurance_policy_number']


def _get_real_plate(resource):
    ''' For testing, we can retrieve the first car out of the database to use its plate
    for the requests that follow. This ensures that we get a "found" result. '''
    url = resource + '?$limit=1'
    response_list = _get_resource(url)
    return response_list[0]['dmv_license_plate_number']


def get_real_tlc_plate():
    return _get_real_plate(FHV_VEHICLE_RESOURCE)


def get_real_yellow_plate():
    return _get_real_plate(MEDALLION_VEHICLE_RESOURCE)
