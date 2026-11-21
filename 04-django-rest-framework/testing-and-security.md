# DRF Automated Testing & API Security Guide

## Module Overview
This guide covers **APITestCase**, testing authenticated endpoints with `force_authenticate`, assertNumQueries, and security testing.

---

## Writing High-Performance Tests with `APITestCase`

```python
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from .models import Order

class OrderAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.order = Order.objects.create(user=self.user, total_amount=1500)

    def test_unauthenticated_access_rejected(self):
        """Unauthenticated requests must be blocked with HTTP 401"""
        response = self.client.get("/api/v1/orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_orders(self):
        """Authenticated users can view their orders"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/v1/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_query_count_prevents_n_plus_one(self):
        """Guarantees endpoint executes <= 2 SQL queries regardless of item count"""
        self.client.force_authenticate(user=self.user)
        with self.assertNumQueries(2):
            self.client.get("/api/v1/orders/")
```
