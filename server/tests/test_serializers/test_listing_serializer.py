# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories

class TestListingSerializer(TestCase):
    def test_car_has_zipcode(self):
        car = factories.Car.create()
        self.assertIsNotNone(serializers.ListingSerializer(car).data['zipcode'])
        self.assertEqual(car.owner.zipcode, serializers.ListingSerializer(car).data['zipcode'])

    def test_car_without_image(self):
        car = factories.Car.create()
        self.assertEqual(self._image_url_for(car), None)

    def test_car_with_image(self):
        filename = 'cat_eating_a_taco.jpg'
        make_model = factories.MakeModel.create(image_filenames=filename)
        car = factories.Car.create(make_model=make_model)

        expected = 'https://s3.amazonaws.com/images.idlecars.com/' + filename
        self.assertEqual(self._image_url_for(car), expected)

    def _image_url_for(self, car):
        return serializers.ListingSerializer(car).data['image_url']
