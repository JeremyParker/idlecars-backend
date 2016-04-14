# from rest_framework.test import APITestCase, APIClient

# from django.core.urlresolvers import reverse
# from .models import UserMessage

# Create your tests here.


# class AboutPageTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = reverse('website:about')
#         self.data = {'first_name': 'Tom', 'email': 'test@test.com', 'message': 'test!'}
#         self.response = self.client.post(self.url, self.data)

#     def test_user_message_create_record(self):
#         self.assertEqual(UserMessage.objects.count(), 1)

#     def test_user_message_send_email_to_ops(self):
#         from django.core.mail import outbox
#         self.assertEqual(len(outbox), 1)
#         self.assertEqual(
#             outbox[0].subject,
#            'A new message from user {}'.format(self.data['first_name']),
#         )
