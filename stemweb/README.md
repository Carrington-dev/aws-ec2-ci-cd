### **4. API Tests (Django REST Framework - DRF)**
Django REST Framework (DRF) provides powerful tools for testing APIs. You can use `APITestCase` from `rest_framework.test` to write unit and integration tests for your API endpoints.  

#### **4.1 Setup for API Testing**
Make sure you have DRF installed in your Django project:  
```bash
pip install djangorestframework
```
Then, add `'rest_framework'` to your `INSTALLED_APPS` in `settings.py`:  
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    ...
    'rest_framework',
]
```

---

#### **4.2 Example API Test Cases**
##### **4.2.1 Testing a Simple GET Request**
If you have an API endpoint that returns a list of items, you can test it like this:
```python
from rest_framework.test import APITestCase
from django.urls import reverse
from myapp.models import Item

class ItemAPITestCase(APITestCase):
    def setUp(self):
        Item.objects.create(name="Laptop", price=1500)
        Item.objects.create(name="Phone", price=800)

    def test_get_items(self):
        url = reverse('item-list')  # Assuming you have a view named "item-list"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Laptop")
```

---

##### **4.2.2 Testing POST Request (Creating an Item)**
If your API allows creating new items via a `POST` request:
```python
class CreateItemTest(APITestCase):
    def test_create_item(self):
        url = reverse('item-list')  # API endpoint for creating an item
        data = {'name': 'Tablet', 'price': 1200}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Tablet')
```
📌 *Note: Always include `format='json'` when sending JSON data.*

---

##### **4.2.3 Testing Authentication & Authorization**
If your API requires authentication, use Django’s `force_authenticate` or `self.client.credentials()`.  

- Example with `force_authenticate`:
```python
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class AuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
    
    def test_authenticated_access(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('protected-endpoint')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
```

- Example with `JWT Authentication`:
```python
from rest_framework_simplejwt.tokens import RefreshToken

class JWTAuthTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_jwt_protected_route(self):
        url = reverse('protected-endpoint')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
```
📌 *Make sure you have `djangorestframework_simplejwt` installed for JWT auth:*
```bash
pip install djangorestframework-simplejwt
```

---

##### **4.2.4 Testing PUT & DELETE Requests**
- **Updating an Item (PUT/PATCH)**:
```python
class UpdateItemTest(APITestCase):
    def setUp(self):
        self.item = Item.objects.create(name="Old Laptop", price=1200)

    def test_update_item(self):
        url = reverse('item-detail', args=[self.item.id])
        data = {'name': 'New Laptop', 'price': 1400}
        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'New Laptop')
```
  
- **Deleting an Item (DELETE)**:
```python
class DeleteItemTest(APITestCase):
    def setUp(self):
        self.item = Item.objects.create(name="Test Item", price=500)

    def test_delete_item(self):
        url = reverse('item-detail', args=[self.item.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Item.objects.count(), 0)
```

---

#### **4.3 Running API Tests**
Run all test cases using:  
```bash
python manage.py test
```
For more detailed test output:  
```bash
python manage.py test --verbosity=2
```

---

Would you like to integrate test automation with CI/CD (e.g., GitHub Actions, GitLab CI)? 🚀