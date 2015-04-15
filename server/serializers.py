# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers

from models import Car


class CarSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    listing_features = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()
    cost_time = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = (
            'id',
            'name',
            'listing_features',
            'cost',
            'cost_time',
        )

    def get_name(self, obj):
        return unicode(obj.make_model)

    def get_listing_features(self, obj):
        return '{} minimum lease, {}, {}, Idlecars Certified'.format(
            obj.min_lease,
            obj.owner.city,
            obj.owner.state_code
        )

    def get_cost(self, obj):
        return unicode(obj.solo_cost)

    def get_cost_time(self, obj):
        return 'a week'
