# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import server.services
from server.models import Car

next_fhv_response = {
    'active': 'YES',
    'base_address': '4301 GLENWOOD ROAD 2ND FLOOR BROOKLYN NY 11210',
    'base_name': 'ABBA LOCAL TRANSPORTATION INC',
    'base_number': 'B90675',
    'base_telephone_number': '(718)444-5125',
    'base_type': 'PARATRANS',
    'certification_date': '2014-04-08T00:00:00',
    'dmv_license_plate_number': 'T650082C',
    'expiration_date': '2016-04-25T00:00:00',
    'hack_up_date': '2014-04-25T00:00:00',
    'last_date_updated': '2015-11-23T00:00:00',
    'last_time_updated': '13:30',
    'license_type': 'FOR HIRE VEHICLE',
    'name': 'FOUR YAR LEASING INC',
    'permit_license_number': 'AA291',
    'reason': 'G',
    'vehicle_license_number': '5536406',
    'vehicle_vin_number': '5TDKK3DC8ES411904',
    'vehicle_year': '2014',
    'wheelchair_accessible': 'WAV',
}

# TODO - a fake response from the tlc database with insurance info


class TestClient(object):
    def __init__(
        self,
        ignored_domain,
        ignmored_token,
        username,
        password,
    ):
        return super(TestClient, self).__init__()

    def get(self, url):
        if 'ERROR' in url:
            raise Car.DoesNotExist
        if server.services.tlc_data_service.FHV_VEHICLE_RESOURCE in url:
            return [next_fhv_response]
        if server.services.tlc_data_service.INSURANCE_RESOURCE in url:
            return [1]
        return []

    def close(self):
        pass
