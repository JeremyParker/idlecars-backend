# # -*- encoding:utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from server.services import make_model_service
from server import factories


class MakeModelServiceTest(TestCase):
    def test_get_image_no_filenames(self):
        make_model = factories.MakeModel()
        img = make_model_service.get_image_url(make_model, 123)
        self.assertIsNone(img)

    def test_get_image_no_key(self):
        make_model = factories.MakeModelWithImages()
        img = make_model_service.get_image_url(make_model)
        self.assertTrue(make_model.image_filenames[0] in img)

    def test_get_image_multi_images(self):
        make_model = factories.MakeModelWithImages()
        img1 = make_model_service.get_image_url(make_model, 143)
        img2 = make_model_service.get_image_url(make_model, 144)
        self.assertNotEqual(img1, img2)

    def test_get_image_single_image(self):
        make_model = factories.MakeModelWithImage()
        img = make_model_service.get_image_url(make_model, 143)
        self.assertTrue(make_model.image_filenames in img)
