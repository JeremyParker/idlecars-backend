# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import server.services
from server.models import Car


next_response = {
    'agent_address': '54-11 QUEENS BOULEVARD WOODSIDE NY 11377',
    'agent_name': 'TAXIFLEET MANAGEMENT LLC',
    'agent_number': '307',
    'agent_telephone_number': '(718)779-5000',
    'current_status': 'CUR',
    'dmv_license_plate_number': '3A15A',
    'last_updated_date': '2015-02-27T00:00:00',
    'last_updated_time': '13:20',
    'license_number': '3A15',
    'medallion_type': 'NAMED DRIVER',
    'model_year': '2012',
    'name': 'THERMILDOR, JELON',
    'type': 'MEDALLION',
    'vehicle_type': 'HYB',
    'vehicle_vin_number': '4T1BD1FK3CU050119'
}


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
        if server.services.tlc_data_service.MEDALLION_VEHICLE_RESOURCE in url:
            return [next_response]
        print 'Someone made an unknown request to our fake TLC data client.'

    def close(self):
        pass
