# -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server import serializers, factories

class TestCarSerializer(TestCase):
    def test_car_without_image(self):
        car = factories.Car()
        self.assertEqual(self._image_url_for(car), None)

    def test_car_with_image(self):
        filename = 'cat_eating_a_taco.jpg'
        make_model = factories.MakeModel(image_filename=filename)
        car = factories.Car(make_model=make_model)

        expected = 'https://s3.amazonaws.com/images.idlecars.com/' + filename
        self.assertEqual(self._image_url_for(car), expected)

    def _image_url_for(self, car):
        return serializers.CarSerializer(car).data['image_url']
