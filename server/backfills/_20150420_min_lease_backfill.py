# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server import models

def run_backfill():
    '''
    replace existing values for min_lease with the new equivalent
    '''
    min_lease_map = {
                '_0_unknown': '_00_unknown',
                '_1_no_min': '_01_no_min',
                '_2_one_week': '_02_one_week',
                '_3_two_weeks': '_03_two_weeks',
                '_4_three_weeks': '_04_three_weeks',
                '_5_one_month': '_05_one_month',
                '_6_six_weeks': '_06_six_weeks',
                '_7_two_months': '_07_two_months',
    }
    for car in models.Car.objects.all():
        if car.min_lease in min_lease_map.keys():
            car.min_lease = min_lease_map[car.min_lease]
            car.save()
