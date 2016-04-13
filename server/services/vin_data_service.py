# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

import requests
import json

from server.models import Car, MakeModel


def lookup_vin_data(car):
    vin_data = _request_vin_data(car.vehicle_vin_number)
    if not vin_data:
        return

    make_name = vin_data['make']['name']
    model_name = vin_data['model']['name']
    make_models = MakeModel.objects.filter(make=make_name, model=model_name)
    if make_models:
        car.make_model = make_models[0]
    else:
        car.make_model = MakeModel.objects.create(
            make=make_name,
            model=model_name,
        )

    try:
        if vin_data['categories']['market'].lower() == 'hybrid':
            car.hybrid = True
    except KeyError:
        pass


def _request_vin_data(vin):
    session = requests.Session()
    uri = 'https://api.edmunds.com/api/vehicle/v2/vins/' + vin + '?fmt=json&api_key=srqpb2wgab7yky57d7nf785s'
    response = session.get(uri)
    if response.status_code != 200:
        raise Car.DoesNotExist

    content_type = response.headers.get('content-type').strip().lower()
    if 'application/json' in content_type:
        return response.json()

    return None
