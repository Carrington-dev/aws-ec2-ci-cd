from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from news.models import Post

class ItemTestCase(TestCase):
    def setUp(self):
        Post.objects.create(title="Test Post 1", author = "Carrington Muleya",  content = "Test Post 1")

    def test_item_price(self):
        item = Post.objects.get(title="Test Post 1")
        self.assertEqual(item.author, "Carrington Muleya")


class APITests(APITestCase):
    def test_get_items(self):
        response = self.client.get(reverse('post-list'))
        self.assertEqual(response.status_code, 200)