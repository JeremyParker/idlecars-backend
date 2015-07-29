# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from server.models import MakeModel

def _data():
    return (
        ('Audi', 'Q5', 1, 1,),
        ('Buick', 'Lacrosse', 0, 1,),
        ('Cadillac', 'CTS', 0, 1,),
        ('Cadillac', 'Escalade', 1, 1,),
        ('Cadillac', 'XTS', 0, 1,),
        ('Chevrolet', 'Impala', 0, 0,),
        ('Chevrolet', 'Malibu', 0, 0,),
        ('Chevrolet', 'MPV', 1, 0,),
        ('Chevrolet', 'MVP', 1, 0,),
        ('Chevrolet', 'Suburban', 1, 1,),
        ('Chevrolet', 'Suburban LT', 1, 1,),
        ('Chevrolet', 'Suburban LTZ', 1, 1,),
        ('Chevrolet', 'Tahoe', 1, 1,),
        ('Chrysler', '300', 0, 0,),
        ('Dodge', 'Journey', 1, 0,),
        ('Ford', 'Expedition', 1, 0,),
        ('Ford', 'Fusion', 0, 0,),
        ('Ford', 'Fusion', 0, 0,),
        ('Ford', 'Taurus', 0, 0,),
        ('GMC', 'Yukon', 1, 1,),
        ('GMC', 'Yukon Denali', 1, 1,),
        ('GMC', 'Yukon XL', 1, 1,),
        ('Honda', 'Accord', 0, 0,),
        ('Honda', 'Accord Hybrid', 0, 0,),
        ('Honda', 'Odyssey', 1, 0,),
        ('Honda', 'Pilot', 1, 0,),
        ('Hyundai', 'Sonata', 0, 0,),
        ('Infiniti', 'JX', 0, 1,),
        ('Lexus', 'ES 300H', 0, 1,),
        ('Lincoln', 'MKS', 0, 0,),
        ('Lincoln', 'MKT', 0, 1,),
        ('Lincoln', 'MKZ', 0, 0,),
        ('Lincoln', 'Navigator', 1, 1,),
        ('Lincoln', 'Navigator', 1, 1,),
        ('Lincoln', 'Town Car', 0, 0,),
        ('Mercedes', 'GL450', 1, 1,),
        ('Mercedes', 'R350', 1, 1,),
        ('Mercedes', 'S550', 0, 1,),
        ('Mercedes-Benz', 'GL 450', 1, 1,),
        ('Mercedes-Benz', 'S-Class', 0, 1,),
        ('Nissan', 'Altima', 0, 0,),
        ('Nissan', 'Altima', 0, 0,),
        ('Nissan', 'Armada', 1, 1,),
        ('Nissan', 'Murano', 1, 0,),
        ('Nissan', 'Murano', 1, 0,),
        ('Nissan', 'Rogue', 1, 0,),
        ('Toyota', 'Avalon', 0, 0,),
        ('Toyota', 'Camry', 0, 0,),
        ('Toyota', 'Camry Hybrid', 0, 0,),
        ('Toyota', 'Highlander', 1, 0,),
        ('Toyota', 'Prius', 0, 0,),
        ('Toyota', 'Prius', 0, 0,),
        ('Toyota', 'Seqouia', 1, 0,),
        ('Toyota', 'Sienna', 1, 0,),
    )

def run_backfill():
    for make, model, body_type, lux_level in _data():
        try:
            mm = MakeModel.objects.get(make=make, model=model)
            mm.lux_level = lux_level
            mm.body_type = body_type
            mm.save()
            print '👌: {} {}'.format(make, model)
        except:
            print 'failed: {} {}'.format(make, model)
