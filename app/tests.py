from unittest import TestCase

from django.test import Client


class MyCase(TestCase):
    def test_auth(self):
        c = Client()
        response = c.post('/auth/', {'login': 'nastya', 'password': '123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
