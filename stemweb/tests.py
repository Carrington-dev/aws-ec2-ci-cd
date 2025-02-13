from django.test import TestCase
from django.urls import reverse

class ViewTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome")
