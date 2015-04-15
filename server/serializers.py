# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = (
            'id',
            'next_available_date',
            'year',
            'solo_cost',
            'solo_deposit',
            'split_cost',
            'split_deposit',
            'min_lease',
        )
        depth = 1
